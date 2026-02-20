from flask import Flask, render_template, request

# NEX-01
app = Flask(__name__)

PRINTABLE_ASCII = ''.join(chr(code) for code in range(32, 127))


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


# NEX-05
@app.route('/', methods=['GET', 'POST'])
def index():
    module = 'caesar'
    operation = 'encrypt'
    shift = 3
    charset = PRINTABLE_ASCII
    text = ''
    output = ''
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

        if not charset:
            error = 'El conjunto de caracteres no puede estar vacío.'
        else:
            if module == 'caesar':
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

    return render_template(
        'index.html',
        module=module,
        operation=operation,
        shift=shift,
        charset=charset,
        printable_ascii=PRINTABLE_ASCII,
        text=text,
        output=output,
        error=error,
        info=info,
    )


# NEX-06
if __name__ == '__main__':
    app.run(debug=True)
