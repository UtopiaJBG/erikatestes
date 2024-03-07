import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil import parser

def load_data():
    try:
        df = pd.read_csv("planilha.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Remedio", "Data de Validade", "Quantia", "Preco por Unidade", "Preco por Subunidade"])
    
    # Verifica se a coluna "Data de Validade" contém algum valor nulo
    if df["Data de Validade"].isnull().any():
        # Se sim, retorne o DataFrame sem alterações
        return df
    
    # Converte a coluna "Data de Validade" para o formato datetime
    df["Data de Validade"] = pd.to_datetime(df["Data de Validade"], errors='coerce')
    
    # Converte a coluna "Data de Validade" de volta para o formato desejado "%d/%m/%Y"
    df["Data de Validade"] = df["Data de Validade"].dt.strftime("%d/%m/%Y")
    
    return df
def import_spreadsheet():
    uploaded_file = st.file_uploader("Escolha o arquivo CSV para importar", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Planilha importada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao importar a planilha: {e}")
            df = pd.DataFrame(columns=["Remedio", "Data de Validade", "Quantia", "Preco por Unidade", "Preco por Subunidade"])

        return df

def save_data(df):
    df.to_csv("planilha.csv", index=False)

def get_current_date():
    return datetime.now().date()

def main():
    st.title("Gestão de Medicamentos")


    # Add a button to import a spreadsheet
    if st.button("Importar Planilha"):
        df = import_spreadsheet()
        # Save the imported data to the CSV file
        save_data(df)
    else:
        # If the button is not clicked, load the data from the CSV file
        df = pd.read_csv("planilha.csv", error_bad_lines=False)
        
        
    menu = ["Adicionar Medicamento", "Editar Medicamento", "Excluir Medicamento", "Visualizar Medicamentos", "Custos da Cirurgia ou Procedimento","Filtrar Medicamentos por Data de Validade"]
    choice = st.sidebar.selectbox("Selecione uma opção:", menu)
    if choice == "Adicionar Medicamento":
        st.header("Adicionar Medicamento")

        remedio = st.text_input("Nome do Medicamento:")
        data_validade = st.date_input("Data de Validade:", value=get_current_date(), format="DD/MM/YYYY")
        quantia = st.number_input("Quantidade:", min_value=1, step=1)
        preco_por_unidade = st.number_input("Preço por Unidade:", min_value=0.01, step=0.01)
        num_subunidades = st.number_input("Número de Subunidades:", min_value=1, step=1)

        preco_por_subunidade = preco_por_unidade / num_subunidades if num_subunidades > 0 else 0

        # Adiciona automaticamente a data de validade ao nome do medicamento
        remedio_com_data = f"{remedio} - {data_validade.strftime('%d-%m-%Y')}"  
        novo_dado = {"Remedio": remedio_com_data, "Data de Validade": data_validade, "Quantia": quantia,
                     "Preco por Unidade": preco_por_unidade, "Preco por Subunidade": preco_por_subunidade}

        if st.button("Adicionar"):
            df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
            save_data(df)
            st.success("Medicamento adicionado com sucesso!")

    elif choice == "Filtrar Medicamentos por Data de Validade":
        st.subheader("Filtrar Medicamentos por Data de Validade")
            
        data_inicio = st.date_input("Data Inicial:")
        data_fim = st.date_input("Data Final:")
    
         # Converte as datas para o formato esperado pelo pandas
        data_inicio = parser.parse(str(data_inicio)).strftime("%Y-%m-%d")
        data_fim = parser.parse(str(data_fim)).strftime("%Y-%m-%d")
    
        medicamentos_filtrados = df[(df["Data de Validade"] >= data_inicio) & (df["Data de Validade"] <= data_fim)]
    
            # Exibe medicamentos filtrados e formata as datas
        st.write(medicamentos_filtrados.assign(**{"Data de Validade": medicamentos_filtrados["Data de Validade"]}))
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

    elif choice == "Custos da Cirurgia ou Procedimento":
        st.header("Custos da Cirurgia ou Procedimento")
    
        if st.checkbox("Mostrar Medicamentos"):
            st.write(df)
    
        medicamentos_selecionados = st.multiselect("Selecione os medicamentos utilizados:", df["Remedio"].unique())
    
        # Criar DataFrame para armazenar informações da tabela
        tabela_quantidades = pd.DataFrame(columns=["Remedio", "Quantidade Total", "Quantidade de Subunidades", "Preco Total"])
    
        for remedio in medicamentos_selecionados:
            st.subheader(f"Informações para {remedio}")
            medicamento_info = df[df["Remedio"] == remedio].iloc[0]
    
            preco_por_unidade = float(medicamento_info["Preco por Unidade"])
            preco_por_subunidade = float(medicamento_info["Preco por Subunidade"]) if "Preco por Subunidade" in medicamento_info else 0
            quantidade_disponivel = float(medicamento_info["Quantia"])
    
            quantidade_utilizada = st.number_input(f"Quantidade Total Utilizada de {remedio}:", min_value=0, step=1)
    
            # Adiciona um campo para informar quantas subunidades foram utilizadas
            quantidade_subunidades_utilizadas = st.number_input(f"Quantidade Total de Subunidades Utilizadas de {remedio}:", min_value=0, step=1)
    
            # Verifica se há unidades ou subunidades suficientes disponíveis
            if quantidade_utilizada > quantidade_disponivel:
                st.warning(f"Quantidade insuficiente de {remedio}. Disponível: {quantidade_disponivel} unidades/subunidades.")
                
                # Adiciona um campo para informar quantas subunidades foram utilizadas
                num_subunidades_utilizadas = st.number_input(f"Quantas subunidades foram utilizadas para {quantidade_utilizada} unidades de {remedio}?", min_value=1, step=1)
                quantidade_utilizada = quantidade_utilizada * num_subunidades_utilizadas
            else:
                # Calcula o preço total com base na quantidade utilizada
                preco_item = quantidade_utilizada * preco_por_unidade + quantidade_subunidades_utilizadas * preco_por_subunidade
    
                # Adiciona as informações à tabela_quantidades
                tabela_quantidades = pd.concat([tabela_quantidades, pd.DataFrame([{
                    "Remedio": remedio,
                    "Quantidade Total": quantidade_utilizada,
                    "Quantidade de Subunidades": quantidade_subunidades_utilizadas,
                    "Preco Total": preco_item
                }])], ignore_index=True)
    
        # Exibe a tabela_quantidades no final
        st.subheader("Tabela de Quantidades e Preços")
        st.write(tabela_quantidades)
    
        # Exibe o preço total da cirurgia ou procedimento no final
        preco_total_cirurgia = tabela_quantidades["Preco Total"].sum()
        st.subheader(f"Preço Total da Cirurgia ou Procedimento: R$ {preco_total_cirurgia:.2f}")
        
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')
        csv = convert_df(df)
        st.download_button(
       "Download CSV Fonte",
       csv,
       "planilha.csv",
       "text/csv",
   key='download-csv'
) 
    # ... (restante do código)
if __name__ == "__main__":
    main()

