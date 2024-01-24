import base64


def save_xml_file(xml_content_base64):
    try:
        xml_content = base64.b64decode(xml_content_base64).decode('utf-8')

        with open('arquivo.xml', 'w') as file:
            file.write(xml_content)

        return 'Arquivo XML recebido, Pronto para importar para a base de dados!'
    except Exception as e:
        return f"Erro ao processar a solicitação: {str(e)}"
