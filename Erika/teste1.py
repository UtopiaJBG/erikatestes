import streamlit as st
import pandas as pd
from datetime import datetime  # Import datetime module

def load_data():
    try:
        df = pd.read_csv("planilha.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Remedio", "Data de Validade", "Quantia"])
    df["Data de Validade"] = pd.to_datetime(df["Data de Validade"])
    df["Data de Validade"] = df["Data de Validade"].dt.strftime("%d/%m/%Y")    
    return df

def save_data(df):
    df.to_csv("planilha.csv", index=False)

def get_current_date():
    return datetime.now().date()  # Get current date

def main():
    st.title("Gestão de Medicamentos")

    df = load_data()

    menu = ["Adicionar Medicamento", "Editar Medicamento", "Excluir Medicamento", "Visualizar Medicamentos", "Gastos na Cirurgia"]
    choice = st.sidebar.selectbox("Selecione uma opção:", menu)

    if choice == "Adicionar Medicamento":
        st.header("Adicionar Medicamento")

        remedio = st.text_input("Nome do Medicamento:")
        data_validade = st.date_input("Data de Validade:", value=get_current_date(), format="DD/MM/YYYY")
        quantia = st.number_input("Quantidade:", min_value=1, step=1)
        preco_unidade = st.number_input("Preço por Unidade:")
        preco_por_pilula = 0
        pilulas_por_unidade = 1

        if st.checkbox("Medicamento em pílulas"):
            preco_por_pilula = st.number_input("Preço por Pílula:")
            pilulas_por_unidade = st.number_input("Quantidade de Pílulas por Unidade:", min_value=1, step=1)

        remedio_com_data = f"{remedio} - {data_validade.strftime('%d-%m-%Y')}"
        novo_dado = {"Remedio": remedio_com_data, "Data de Validade": data_validade, "Quantia": quantia,
                     "Preco por Unidade": preco_unidade, "Preco por Pilula": preco_por_pilula,
                     "Pilulas por Unidade": pilulas_por_unidade}

        if st.button("Adicionar"):
            df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
            save_data(df)
            st.success("Medicamento adicionado com sucesso!")
    elif choice == "Editar Medicamento":
        st.header("Editar Medicamento")

        if st.checkbox("Mostrar Medicamentos"):
            st.write(df)

        busca_medicamento_editar = st.text_input("Digite o nome do medicamento que deseja editar:")
        medicamentos_filtrados_editar = df[df["Remedio"].str.contains(busca_medicamento_editar, case=False, na=False)]

        if not medicamentos_filtrados_editar.empty:
            st.write(medicamentos_filtrados_editar)
        else:
            st.warning("Nenhum medicamento encontrado com o nome digitado.")

        remedio_para_editar = st.selectbox("Escolha o medicamento para editar:", medicamentos_filtrados_editar["Remedio"].unique(), key="editar_medicamento")
        indice_para_editar = df[df["Remedio"] == remedio_para_editar].index

        if st.button("Mostrar Detalhes do Medicamento"):
            if not indice_para_editar.empty:
                detalhes = df.loc[indice_para_editar]
                st.write(detalhes)
            else:
                st.warning("Medicamento não encontrado. Certifique-se de escolher um medicamento válido.")

        quantidade_utilizada = st.number_input("Quantidade Utilizada:", min_value=0, step=1)

        if st.button("Atualizar Quantidade Utilizada"):
            if not indice_para_editar.empty:
                if "Quantia Utilizada" not in df.columns:
                    df["Quantia Utilizada"] = 0  # Adiciona a coluna se ainda não existir
                    df.loc[indice_para_editar, "Quantia Utilizada"] += quantidade_utilizada
        
            # Verifica se a coluna "Quantia" existe antes de tentar atualizar
            if "Quantia" in df.columns:
                df.loc[indice_para_editar, "Quantia"] -= quantidade_utilizada
                save_data(df)
                st.success(f"{quantidade_utilizada} unidades do medicamento foram utilizadas com sucesso!")
        else:
            st.write()
    elif choice == "Visualizar Medicamentos":
        st.header("Visualizar Medicamentos")

        if not df.empty:
            st.write()
        else:
            st.warning("Nenhum medicamento cadastrado.")

        if not df.empty:
            busca_usuario = st.text_input("Digite o nome do medicamento para buscar:")
            medicamentos_filtrados = df[df["Remedio"].str.contains(busca_usuario, case=False, na=False)]

            if medicamentos_filtrados.empty:
                st.warning("Nenhum medicamento encontrado com o nome digitado.")
            else:
                # Garanta que a coluna "Data de Validade" seja do tipo datetime
                medicamentos_filtrados["Data de Validade"] = (medicamentos_filtrados["Data de Validade"])

                # Exibe medicamentos filtrados e formata as datas
                st.write(medicamentos_filtrados.assign(**{"Data de Validade": medicamentos_filtrados["Data de Validade"]}))
        else:
            st.warning("Nenhum medicamento cadastrado.")

        st.subheader("Filtrar Medicamentos por Data de Validade")
        data_inicio = st.date_input("Data Inicial:")
        data_fim = st.date_input("Data Final:")

        df["Data de Validade"] = pd.to_datetime(df["Data de Validade"])

        medicamentos_filtrados = df[(df["Data de Validade"] >= pd.Timestamp(data_inicio)) & (df["Data de Validade"] <= pd.Timestamp(data_fim))]

        # Exibe medicamentos filtrados e formata as datas
        st.write(medicamentos_filtrados.assign(**{"Data de Validade": medicamentos_filtrados["Data de Validade"]}))

    elif choice == "Excluir Medicamento":
        st.header("Excluir Medicamento")

        st.write(df)

        # Adicione um botão para excluir todos os medicamentos com quantidade zero
        if st.button("Excluir Medicamentos com Quantidade 0"):
            df = df[df["Quantia"] > 0]
            save_data(df)
            st.success("Medicamentos com quantidade zero foram excluídos com sucesso!")
        # Use a função autocomplete para fornecer sugestões
        remedios_sugeridos = df["Remedio"].unique()
        remedio_selecionado = st.selectbox("Selecione o medicamento que deseja excluir:", remedios_sugeridos)

        if st.button("Excluir Medicamento"):
            if remedio_selecionado is not None:
                df = df[df["Remedio"] != remedio_selecionado]
                save_data(df)
                st.success(f"Medicamento '{remedio_selecionado}' excluído com sucesso!")
            else:
                st.warning("Por favor, escolha um medicamento válido.")
            
    elif choice == "Gastos na Cirurgia":
        st.header("Gastos na Cirurgia")

        # Lógica para lidar com os gastos na cirurgia
        valor_cirurgia = st.number_input("Valor total da cirurgia:")
        num_pilulas = st.number_input("Quantidade de pílulas utilizadas na cirurgia:", min_value=1, step=1)

        # Calcula o preço por pílula
        preco_por_pilula = valor_cirurgia / num_pilulas

        st.info(f"O preço por pílula é: R$ {preco_por_pilula:.2f}")

        if st.button("Registrar Gastos"):
            novo_dado = {"Remedio": "Gastos na Cirurgia", "Quantia": num_pilulas}
            df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
            save_data(df)
            st.success("Gastos na cirurgia registrados com sucesso!")
if __name__ == "__main__":
    main()