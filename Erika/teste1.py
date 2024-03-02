import streamlit as st
import pandas as pd
from datetime import datetime
import subprocess
def execute_git_commands():
    # Comandos Git desejados
    subprocess.run(["git", "clone", "https://seu-usuario@github.com/seu-repositorio.git"])
   
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

def save_data(df):
    df.to_csv("planilha.csv", index=False)

def get_current_date():
    return datetime.now().date()

def main():
    st.title("Gestão de Medicamentos")

    df = load_data()

    menu = ["Adicionar Medicamento", "Editar Medicamento", "Excluir Medicamento", "Visualizar Medicamentos", "Custos da Cirurgia ou Procedimento"]
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
        def git_commands():
            # Comando Git: git add *
            subprocess.run(["git", "add", "*"])
        
            # Comando Git: git commit -m "a"
            subprocess.run(["git", "commit", "-m", "a"])
        
            # Comando Git: git push
            subprocess.run(["git", "push"])
        
        # Interface do Streamlit
        st.title("Git Commands in Streamlit")
        
        # Botão para acionar os comandos Git
        if st.button("Execute Git Commands"):
            git_commands()
            st.success("Comandos Git executados com sucesso!")

    # ... (restante do código)
if __name__ == "__main__":
    main()