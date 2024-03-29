import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil import parser
import requests
from io import StringIO


original_quantia_atual = 0
output_csv_path = "planilha1.csv"

def load_data_from_github():
    csv_url = "https://raw.githubusercontent.com/UtopiaJBG/erikatestes/main/Erika/planilha.csv"
    try:
        # Baixa o conteúdo do arquivo CSV usando requests
        response = requests.get(csv_url)
        # Verifica se a requisição foi bem-sucedida
        response.raise_for_status()
        # Lê o conteúdo baixado no Pandas DataFrame
        df = pd.read_csv(StringIO(response.text), parse_dates=["Data de Validade"], dayfirst=True, encoding='utf-8', sep=';')
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao carregar dados do GitHub: {e}")
        return pd.DataFrame()

# Função para carregar os dados do arquivo local "planilha1.csv"
def load_data_locally():
    file_path = "planilha1.csv"
    try:
        # Lê o conteúdo do arquivo CSV no Pandas DataFrame
        df = pd.read_csv(file_path, parse_dates=["Data de Validade"], dayfirst=True, encoding='utf-8')
        df["Data de Validade"] = pd.to_datetime(df["Data de Validade"], errors='coerce')

        return df
    except FileNotFoundError:
        st.warning(f"Arquivo '{file_path}' não encontrado. Você pode copiar os dados do GitHub primeiro.")
        return pd.DataFrame()

# Função para salvar os dados no arquivo local "planilha1.csv"
def save_data_locally(df):
    file_path = "planilha1.csv"
    df.to_csv(file_path, index=False, encoding='utf-8')   
    return file_path


def calcular_quantias_restantes(original_quantia_atual, num_subunidades, subunidade_utilizada): 
    quantia_restante = ((original_quantia_atual * num_subunidades) - subunidade_utilizada) / num_subunidades      
    return quantia_restante


def get_current_date():
    return datetime.now().date()


def main():
    st.title("Gestão de Medicamentos")

    # Carrega os dados localmente
    df = load_data_locally()

    

    menu = ["Adicionar Medicamento", "Editar Medicamento", "Excluir Medicamento", "Visualizar Medicamentos", "Custos da Cirurgia ou Procedimento","Filtrar Medicamentos por Data de Validade","Carregar Dados do GitHub"]
    choice = st.sidebar.selectbox("Selecione uma opção:", menu)
    if choice == "Adicionar Medicamento":
        st.image("Erika/logo.png",  width=400)

        st.header("Adicionar Medicamento")

        remedio = st.text_input("Nome do Medicamento:")
        data_validade = st.date_input("Data de Validade:", value=get_current_date(), format="DD/MM/YYYY")
        quantia = st.number_input("Quantidade:", min_value=1, step=1)
        preco_por_unidade = st.number_input("Preço por Unidade:", min_value=0.01, step=0.01)
        num_subunidades = st.number_input("Número de Subunidades:", min_value=1, step=1)

        subunidades_totais = quantia * num_subunidades
        quantia_atual = quantia
        subunidades_restantes = subunidades_totais

        preco_por_subunidade = preco_por_unidade / num_subunidades if num_subunidades > 0 else 0

        # Adiciona automaticamente a data de validade ao nome do medicamento
        remedio_com_data = f"{remedio} - {data_validade.strftime('%d-%m-%Y')}"  
        novo_dado = {"Remedio": remedio_com_data, "Data de Validade": data_validade, "Quantia Inicial": quantia,
                     "Preco por Unidade": preco_por_unidade, "Preco por Subunidade": preco_por_subunidade,
                     "Subunidades Totais": subunidades_totais, "Subunidades Restantes": subunidades_restantes,
                     "Quantia Atual": quantia_atual}

        if st.button("Adicionar"):
            # Converta a data novamente para o formato esperado ao adicionar o novo dado
            novo_dado["Data de Validade"] = pd.to_datetime(novo_dado["Data de Validade"], errors='coerce')

            df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
            save_data_locally(df)
            st.success("Medicamento adicionado com sucesso!")
    elif choice == "Carregar Dados do GitHub":
        st.image("Erika/logo.png",  width=400)

        st.header("Carregar Dados do GitHub")

        if st.button("Copiar dados do GitHub para arquivo local"):
            df_github = load_data_from_github()
            save_data_locally(df_github)
            st.success("Dados copiados do GitHub para 'planilha1.csv'")

    elif choice == "Filtrar Medicamentos por Data de Validade":
        st.image("Erika/logo.png",  width=400)

        st.subheader("Filtrar Medicamentos por Data de Validade")
        
        data_inicio = st.date_input("Data Inicial:")
        data_fim = st.date_input("Data Final:")
    
        # Converte as datas para o formato de datetime
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
    
        # Filtra os medicamentos por data de validade
        medicamentos_filtrados = df[(df["Data de Validade"] >= data_inicio) & (df["Data de Validade"] <= data_fim)]
    
        # Ordena os medicamentos filtrados por data de validade
        medicamentos_filtrados["Data de Validade"] = medicamentos_filtrados["Data de Validade"].dt.strftime('%d/%m/%Y')
        medicamentos_filtrados = medicamentos_filtrados.sort_values(by=["Data de Validade"])
    
        # Exibe medicamentos filtrados e formata as datas
        st.dataframe(medicamentos_filtrados, height=500)

    elif choice == "Visualizar Medicamentos":
        st.image("Erika/logo.png",  width=400)

        columns_to_display = [
            "Remedio",
            "Data de Validade",
            "Quantia Inicial",
            "Preco por Unidade",
            "Preco por Subunidade",
            "Subunidades Totais",
            "Subunidades Restantes",
            "Quantia Atual"]
        st.header("Visualizar Medicamentos")

        if not df.empty:
            st.write()
        else:
            st.warning("Nenhum medicamento cadastrado.")

        if not df.empty:
            busca_usuario = st.text_input("Digite o nome do medicamento para buscar:")
            medicamentos_filtrados = df[df["Remedio"].astype(str).str.contains(busca_usuario, case=False, na=False)]
        
            if medicamentos_filtrados.empty:
                st.warning("Nenhum medicamento encontrado com o nome digitado.")
            else:
                # Ensure that the "Data de Validade" column is of datetime type
                medicamentos_filtrados["Data de Validade"] = pd.to_datetime(medicamentos_filtrados["Data de Validade"])
                # Display filtered medications and format dates
                st.dataframe(medicamentos_filtrados[columns_to_display].assign(**{"Data de Validade": medicamentos_filtrados["Data de Validade"].dt.strftime('%d/%m/%Y')}))
        else:
            st.warning("Nenhum medicamento cadastrado.")
        
    elif choice == "Editar Medicamento":
        st.image("Erika/logo.png",  width=400)

        busca_medicamento_editar = st.text_input("Digite o nome do medicamento que deseja editar:")
        medicamentos_filtrados_editar = df[df["Remedio"].astype(str).str.contains(busca_medicamento_editar, case=False, na=False)]
        
        st.header("Editar Medicamento")
        
        # Ordena os medicamentos filtrados por data de validade
        medicamentos_filtrados_editar["Data de Validade"] = pd.to_datetime(medicamentos_filtrados_editar["Data de Validade"])
        medicamentos_filtrados_editar = medicamentos_filtrados_editar.sort_values(by=["Data de Validade"])
        
        # Converte as datas para o formato esperado pelo pandas
        medicamentos_filtrados_editar["Data de Validade"] = medicamentos_filtrados_editar["Data de Validade"].dt.strftime('%d/%m/%Y')
        
        columns_to_display = [
            "Remedio",
            "Data de Validade",
            "Quantia Inicial",
            "Preco por Unidade",
            "Preco por Subunidade",
            "Subunidades Totais",
            "Subunidades Restantes",
            "Quantia Atual"]
        
        st.dataframe(medicamentos_filtrados_editar[columns_to_display], height=600)
      
        
        if not medicamentos_filtrados_editar.empty:
            st.write()
        else:
            st.warning("Nenhum medicamento encontrado com o nome digitado.")

        remedio_para_editar = st.selectbox("Escolha o medicamento para editar:", medicamentos_filtrados_editar["Remedio"].unique(), key="editar_medicamento")
        indice_para_editar = df[df["Remedio"] == remedio_para_editar].index

        if st.button("Mostrar Detalhes do Medicamento"):
            if not indice_para_editar.empty:
                detalhes = df.loc[indice_para_editar]
                st.dataframe(detalhes[columns_to_display], height=100)
            else:
                st.warning("Medicamento não encontrado. Certifique-se de escolher um medicamento válido.")

        quantia_inicial = df.loc[indice_para_editar, "Quantia Inicial"]
        quantidade_utilizada = st.number_input("Quantidade Utilizada:", min_value=0, step=1)
        quantia_atual = df.loc[indice_para_editar, "Quantia Atual"]
        subunidades_totais = df.loc[indice_para_editar, "Subunidades Totais"]

        if st.button("Quantidade Utilizada"):   
            if "Quantia Atual" in df.columns:
                df.loc[indice_para_editar, "Quantia Atual"] -= quantidade_utilizada
                df.loc[indice_para_editar, "Subunidades Restantes"] = (subunidades_totais / quantia_inicial) * (quantia_atual - quantidade_utilizada) 
                save_data_locally(df)
                st.success(f"{quantidade_utilizada} unidades do medicamento foram utilizadas com sucesso!")

                
        subunidades_utilizadas = st.number_input("Subunidades Utilizadas:", min_value=0, step=1)
        
        if st.button("Subunidades Utilizadas"):
            if "Subunidades Restantes" in df.columns:
                num_subunidades = df.loc[indice_para_editar, "Subunidades Restantes"]
                subunidade_utilizada = subunidades_utilizadas
    
                # Calculate the remaining quantity using the calcular_quantias_restantes function
                df.loc[indice_para_editar, "Quantia Atual"] = df.loc[indice_para_editar, "Quantia Inicial"] * ((df.loc[indice_para_editar, "Quantia Atual"] * (df.loc[indice_para_editar, "Subunidades Totais"] / df.loc[indice_para_editar, "Quantia Inicial"]) - subunidade_utilizada) / df.loc[indice_para_editar, "Subunidades Totais"])
                
                # Update "Subunidades Restantes" based on the remaining quantity
                df.loc[indice_para_editar, "Subunidades Restantes"] -= subunidades_utilizadas
                save_data_locally(df)
                st.success(f"{subunidades_utilizadas} unidades do medicamento foram utilizadas com sucesso!")
        else:
            st.write()
        
        def convert_df(df):
            return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8')
        if st.button("Baixar Planilha"):
            st.download_button(
        "Download Planilha",
        convert_df(df),  # Use a função de conversão para CSV definida anteriormente
        "planilha_medicamentos.csv",
        "text/csv; charset=utf-8-sig",
        key='download-planilha'
    )
            
            
    elif choice == "Excluir Medicamento":
        st.image("Erika/logo.png",  width=400)

        columns_to_display = [
            "Remedio",
            "Data de Validade",
            "Quantia Inicial",
            "Preco por Unidade",
            "Preco por Subunidade",
            "Subunidades Totais",
            "Subunidades Restantes",
            "Quantia Atual"]
        st.header("Excluir Medicamento")

        df["Data de Validade"] = pd.to_datetime(df["Data de Validade"])

        st.dataframe(df[columns_to_display].assign(**{"Data de Validade": df["Data de Validade"].dt.strftime('%d/%m/%Y')}))
        
        # Adicione um botão para excluir todos os medicamentos com quantidade zero
        if st.button("Excluir Medicamentos com Quantidade 0"):
            df = df[df["Quantia"] > 0]
            save_data_locally(df)
            st.success("Medicamentos com quantidade zero foram excluídos com sucesso!")
        # Use a função autocomplete para fornecer sugestões
        remedios_sugeridos = df["Remedio"].unique()
        remedio_selecionado = st.selectbox("Selecione o medicamento que deseja excluir:", remedios_sugeridos)

        if st.button("Excluir Medicamento"):
            if remedio_selecionado is not None:
                df = df[df["Remedio"] != remedio_selecionado]
                save_data_locally(df)
                st.success(f"Medicamento '{remedio_selecionado}' excluído com sucesso!")
            else:
                st.warning("Por favor, escolha um medicamento válido.")

    elif choice == "Custos da Cirurgia ou Procedimento":
        st.header("Custos da Cirurgia ou Procedimento")
  # Get user input for patient's name, type of procedure, and date of the procedure
        nome_paciente = st.text_input("Nome do Paciente:")
        tipo_procedimento = st.text_input("Tipo de Procedimento:")
        data_procedimento = st.date_input("Data do Procedimento:", value=get_current_date(), format="DD/MM/YYYY")
        
    
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
            quantidade_disponivel = float(medicamento_info["Quantia Atual"])
    
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
    
        # Adiciona as informações do paciente à tabela_quantidades
        st.image("Erika/logo.png",  width=400)

        tabela_quantidades["Nome do Paciente"] = nome_paciente
        tabela_quantidades["Tipo de Procedimento"] = tipo_procedimento
        tabela_quantidades["Data do Procedimento"] = data_procedimento.strftime('%d/%m/%Y')
    
        # Exibe o preço total da cirurgia ou procedimento no final
        preco_total_cirurgia = tabela_quantidades["Preco Total"].sum()
        st.subheader(f"Preço Total da Cirurgia ou Procedimento: R$ {preco_total_cirurgia:.2f}")
        st.subheader("Informações do Paciente e Procedimento")
        st.write(f"Nome do Paciente: {nome_paciente}")
        st.write(f"Tipo de Procedimento: {tipo_procedimento}")
        st.write(f"Data do Procedimento: {data_procedimento.strftime('%d/%m/%Y')}")
        def convert_df(df):
            return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8')
        csv = convert_df(tabela_quantidades)
        st.download_button(
    "Download Tabela de Informações",
    csv,
    "tabela_quantidades.csv",
    "text/csv; charset=utf-8-sig",
    key='download-csv'
)
    # ... (restante do código)
if __name__ == "__main__":
    main()
