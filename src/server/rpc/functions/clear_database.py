import psycopg2
def clear_database():
    try:
        # Conexão
        connection = psycopg2.connect(
            user="is",
            password="is",
            host="is-db",
            port="5432",
            database="is"
        )

        cursor = connection.cursor()

        try:
            # Excluir todos os dados das tabelas
            cursor.execute("DELETE FROM disasters;")
            cursor.execute("DELETE FROM countries;")
            cursor.execute("DELETE FROM airplane_disasters;")
            cursor.execute("DELETE FROM imported_documents;")

            connection.commit()
            print("Limpeza da base de dados concluída com sucesso.")
        except Exception as e:
            # Em caso de erro, fazer rollback
            connection.rollback()
            print(f"Erro ao limpar a base de dados: {e}")
        finally:
            cursor.close()

    except Exception as e:
        print(f"Erro de conexão: {e}")
    finally:
        if connection is not None:
            connection.close()
