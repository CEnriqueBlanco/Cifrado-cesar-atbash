import re
import string
import json

from flask import Flask, render_template, request, jsonify

# NEX-01
app = Flask(__name__)

PRINTABLE_ASCII = ''.join(chr(code) for code in range(32, 127))
SPANISH_COMMON_PATTERNS = (
    ' de ',
    ' la ',
    ' el ',
    ' que ',
    ' y ',
    ' en ',
    ' los ',
    ' las ',
    ' por ',
    ' con ',
    ' no ',
    ' una ',
    ' un ',
    ' del ',
    ' al ',
    ' se ',
)

SPANISH_COMMON_WORDS = tuple(pattern.strip() for pattern in SPANISH_COMMON_PATTERNS)
FOCUS_WORDS = ('punto', 'puntos')
AUTO_CHARSETS = (
    ('ASCII imprimible', PRINTABLE_ASCII),
    ('Letras mayúsculas A-Z', string.ascii_uppercase),
    ('Letras minúsculas a-z', string.ascii_lowercase),
    ('Letras A-Z y a-z', string.ascii_letters),
    ('Alfanumérico A-Z a-z 0-9', string.ascii_letters + string.digits),
    ('Español simple (incluye ñ y vocales acentuadas)', 'abcdefghijklmnñopqrstuvwxyzáéíóúü '),
)


# NEX-02
def normalize_charset(charset: str) -> str:
    seen = set()
    unique = []
    for char in charset:
        if char not in seen:
            seen.add(char)
            unique.append(char)
    return ''.join(unique)


# NEX-03
def caesar_cipher(text: str, charset: str, shift: int, decrypt: bool = False) -> str:
    if not charset:
        return text

    size = len(charset)
    shift = shift % size
    if decrypt:
        shift = -shift

    result = []
    for char in text:
        if char in charset:
            index = charset.index(char)
            new_index = (index + shift) % size
            result.append(charset[new_index])
        else:
            result.append(char)
    return ''.join(result)


# NEX-04
def atbash_cipher(text: str, charset: str) -> str:
    if not charset:
        return text

    size = len(charset)
    result = []
    for char in text:
        if char in charset:
            index = charset.index(char)
            mirror_index = size - 1 - index
            result.append(charset[mirror_index])
        else:
            result.append(char)
    return ''.join(result)


# NEX-05A
def score_plaintext_candidate(text: str) -> int:
    normalized = f' {text.lower()} '
    score = 0

    for pattern in SPANISH_COMMON_PATTERNS:
        score += normalized.count(pattern) * 5

    score += sum(char.isalpha() for char in text)
    score += text.count(' ')

    if text:
        printable_ratio = sum(char.isprintable() or char.isspace() for char in text) / len(text)
        score += int(printable_ratio * 10)

    return score


# NEX-05AA
def spanish_word_hits(text: str) -> int:
    normalized = f' {text.lower()} '
    return sum(normalized.count(f' {word} ') for word in SPANISH_COMMON_WORDS)


# NEX-05AB
def focus_word_hits(text: str) -> int:
    return sum(len(re.findall(rf'\b{re.escape(word)}\b', text, flags=re.IGNORECASE)) for word in FOCUS_WORDS)


# NEX-05AC
def best_caesar_candidate(text: str, charset: str, max_shifts: int = 200) -> tuple[int, int, str]:
    if not charset:
        return score_plaintext_candidate(text), 0, text

    max_unique_shifts = min(max_shifts, len(charset))
    plain_score = score_plaintext_candidate(text)
    best_shift = 0
    best_candidate = text
    best_score = plain_score

    for shift in range(1, max_unique_shifts + 1):
        candidate = caesar_cipher(text, charset, shift, decrypt=True)
        candidate_score = score_plaintext_candidate(candidate)
        if candidate_score > best_score:
            best_score = candidate_score
            best_shift = shift
            best_candidate = candidate

    return best_score, best_shift, best_candidate


# NEX-05B
def brute_force_caesar_decrypt_range(
    text: str,
    charset: str,
    start_shift: int = 1,
    count: int = 200,
) -> list[dict[str, str | int]]:
    if start_shift < 1:
        start_shift = 1

    results = []
    end_shift = start_shift + count
    for shift in range(start_shift, end_shift):
        decrypted = caesar_cipher(text, charset, shift, decrypt=True)
        score = score_plaintext_candidate(decrypted)
        hits = spanish_word_hits(decrypted)
        focus_hits = focus_word_hits(decrypted)
        likely_plain = hits >= 2 or score >= max(20, int(len(decrypted) * 0.6))
        results.append(
            {
                'shift': shift,
                'decrypted': decrypted,
                'score': score,
                'hits': hits,
                'focus_hits': focus_hits,
                'has_focus_word': focus_hits > 0,
                'likely_plain': likely_plain,
            }
        )
    return results


# NEX-05C
def detect_encryption_type(text: str, charset: str) -> str:
    plain_score = score_plaintext_candidate(text)

    atbash_candidate = atbash_cipher(text, charset)
    atbash_score = score_plaintext_candidate(atbash_candidate)

    best_caesar_score, best_caesar_shift, best_caesar_text = best_caesar_candidate(text, charset, 200)

    if best_caesar_score <= plain_score + 2 and atbash_score <= plain_score + 2:
        return (
            'No se pudo identificar un cifrado claro.\n\n'
            f'Puntuación base: {plain_score}\n'
            f'Atbash: {atbash_score}\n'
            f'César mejor candidato: desplazamiento {best_caesar_shift} con puntuación {best_caesar_score}\n\n'
            f'Atbash sugerido: {atbash_candidate}\n'
            f'César sugerido: {best_caesar_text}'
        )

    if atbash_score >= best_caesar_score:
        return (
            'Cifrado identificado: Atbash\n\n'
            f'Puntuación: {atbash_score}\n'
            f'Texto sugerido: {atbash_candidate}'
        )

    return (
        'Cifrado identificado: César\n\n'
        f'Desplazamiento sugerido: {best_caesar_shift}\n'
        f'Puntuación: {best_caesar_score}\n'
        f'Texto sugerido: {best_caesar_text}'
    )


# NEX-05CB
def build_auto_charset_candidates(text: str) -> list[dict[str, str | int]]:
    candidates = []
    for charset_name, charset_value in AUTO_CHARSETS:
        normalized_charset = normalize_charset(charset_value)
        if not normalized_charset:
            continue

        atbash_candidate = atbash_cipher(text, normalized_charset)
        atbash_score = score_plaintext_candidate(atbash_candidate)
        candidates.append(
            {
                'method': 'Atbash',
                'charset_name': charset_name,
                'charset_len': len(normalized_charset),
                'shift': 0,
                'score': atbash_score,
                'text': atbash_candidate,
            }
        )

        caesar_score, caesar_shift, caesar_candidate = best_caesar_candidate(text, normalized_charset, 200)
        candidates.append(
            {
                'method': 'César',
                'charset_name': charset_name,
                'charset_len': len(normalized_charset),
                'shift': caesar_shift,
                'score': caesar_score,
                'text': caesar_candidate,
            }
        )

    return sorted(candidates, key=lambda item: int(item['score']), reverse=True)


# NEX-05CA
def detect_encryption_type_auto_charset(text: str) -> tuple[str, list[dict[str, str | int]]]:
    plain_score = score_plaintext_candidate(text)
    ranked_candidates = build_auto_charset_candidates(text)
    top_candidates = ranked_candidates[:5]

    best_method = 'Sin identificar'
    best_charset_name = 'N/A'
    best_charset_value = ''
    best_score = plain_score
    best_shift = 0
    best_candidate = text

    if ranked_candidates:
        best_overall = ranked_candidates[0]
        best_method = str(best_overall['method'])
        best_charset_name = str(best_overall['charset_name'])
        best_charset_value = next(
            (normalize_charset(value) for name, value in AUTO_CHARSETS if name == best_charset_name),
            ''
        )
        best_score = int(best_overall['score'])
        best_shift = int(best_overall['shift'])
        best_candidate = str(best_overall['text'])

    if best_score <= plain_score + 2:
        return (
            'Modo detección: Automática de charset\n'
            'Resultado: No concluyente\n'
            f'Puntuación base: {plain_score}\n'
            f'Mejor charset probado: {best_charset_name}\n'
            f'Longitud charset: {len(best_charset_value)}\n'
            f'Método candidato: {best_method}\n'
            f'Desplazamiento sugerido: {best_shift}\n'
            f'Puntuación: {best_score}\n'
            f'Texto sugerido: {best_candidate}'
        ), top_candidates

    if best_method == 'César':
        return (
            'Modo detección: Automática de charset\n'
            f'Charset sugerido: {best_charset_name}\n'
            f'Longitud charset: {len(best_charset_value)}\n'
            'Cifrado identificado: César\n'
            f'Desplazamiento sugerido: {best_shift}\n'
            f'Puntuación: {best_score}\n'
            f'Texto sugerido: {best_candidate}'
        ), top_candidates

    return (
        'Modo detección: Automática de charset\n'
        f'Charset sugerido: {best_charset_name}\n'
        f'Longitud charset: {len(best_charset_value)}\n'
        'Cifrado identificado: Atbash\n'
        f'Puntuación: {best_score}\n'
        f'Texto sugerido: {best_candidate}'
    ), top_candidates


# NEX-05D
def parse_detect_output_sections(output: str) -> list[dict[str, str]]:
    sections = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ':' in line:
            label, value = line.split(':', 1)
            sections.append(
                {
                    'label': label.strip(),
                    'value': value.strip(),
                }
            )
        else:
            sections.append(
                {
                    'label': 'Detalle',
                    'value': line,
                }
            )
    return sections


# NEX-05
@app.route('/', methods=['GET', 'POST'])
def index():
    module = 'caesar'
    operation = 'encrypt'
    shift = 3
    charset = PRINTABLE_ASCII
    text = ''
    output = ''
    detect_sections = []
    auto_candidates = []
    brute_rows = []
    brute_start = 1
    brute_end = 0
    brute_next_start = 201
    error = ''
    info = ''

    if request.method == 'POST':
        module = request.form.get('module', 'caesar')
        operation = request.form.get('operation', 'encrypt')
        text = request.form.get('text', '')
        charset = request.form.get('charset', PRINTABLE_ASCII)

        normalized = normalize_charset(charset)
        if normalized != charset:
            info = 'Se eliminaron caracteres repetidos en el conjunto de caracteres.'
        charset = normalized

        if operation == 'detect_auto_charset':
            output, auto_candidates = detect_encryption_type_auto_charset(text)
            detect_sections = parse_detect_output_sections(output)
            
            # Si se solicita también brute force, generarlo
            add_brute = request.form.get('add_brute', '0') == '1'
            if add_brute and charset:
                charset_size = len(charset)
                brute_rows = brute_force_caesar_decrypt_range(text, charset, 1, charset_size)
                brute_end = charset_size
                brute_next_start = brute_end + 1
        elif not charset:
            error = 'El conjunto de caracteres no puede estar vacío.'
        else:
            if operation == 'bruteforce_200':
                start_raw = request.form.get('brute_start', '1').strip()
                try:
                    brute_start = int(start_raw)
                except ValueError:
                    brute_start = 1

                if brute_start < 1:
                    brute_start = 1

                # Generar TODOS los desplazamientos posibles del charset
                charset_size = len(charset)
                batch_size = charset_size
                
                brute_rows = brute_force_caesar_decrypt_range(text, charset, brute_start, batch_size)
                brute_end = brute_start + batch_size - 1
                brute_next_start = brute_end + 1
            elif operation == 'detect':
                output = detect_encryption_type(text, charset)
                detect_sections = parse_detect_output_sections(output)
                
                # Si se solicita also brute force, generarlo
                add_brute = request.form.get('add_brute', '0') == '1'
                if add_brute:
                    charset_size = len(charset)
                    brute_rows = brute_force_caesar_decrypt_range(text, charset, 1, charset_size)
                    brute_end = charset_size
                    brute_next_start = brute_end + 1
            elif module == 'caesar':
                shift_raw = request.form.get('shift', '3').strip()
                try:
                    shift = int(shift_raw)
                except ValueError:
                    error = 'La llave de César debe ser un número entero.'
                else:
                    output = caesar_cipher(
                        text,
                        charset,
                        shift,
                        decrypt=(operation == 'decrypt')
                    )
            elif module == 'atbash':
                output = atbash_cipher(text, charset)
            else:
                error = 'Módulo no válido.'

    # Si se solicita brute force vía AJAX, devolver JSON
    add_brute = request.form.get('add_brute', '0') == '1'
    if add_brute and brute_rows and request.method == 'POST':
        return jsonify({
            'success': True,
            'brute_rows': brute_rows,
            'brute_start': brute_start,
            'brute_end': brute_end,
            'charset_size': len(charset)
        })
    
    return render_template(
        'index.html',
        module=module,
        operation=operation,
        shift=shift,
        charset=charset,
        charset_size=len(charset),
        printable_ascii=PRINTABLE_ASCII,
        text=text,
        output=output,
        detect_sections=detect_sections,
        auto_candidates=auto_candidates,
        brute_rows=brute_rows,
        brute_start=brute_start,
        brute_end=brute_end,
        brute_next_start=brute_next_start,
        error=error,
        info=info,
    )


# NEX-06
if __name__ == '__main__':
    app.run(debug=True)
