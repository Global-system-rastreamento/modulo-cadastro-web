import streamlit as st
from app.services.report_service.report_service import process_report
from app.src.funcs import get_vehicles_for_client

@st.dialog("Relatório de Quilometragem e Infrações")
def report_dialog():
    """
    Exibe um diálogo para configurar e gerar o relatório de quilometragem e infrações.
    """
    client_name = st.session_state.get("client_name", "Cliente Desconhecido")
    client_id = st.session_state.get("client_id", "ID Desconhecido") # Recupera o ID do cliente
    all_vehicles_dict = {}

    if not st.session_state.get("all_vehicles", ""):
        vehicles = get_vehicles_for_client(client_id)
        if not vehicles:
            vehicles = []

        vehicle_list_str = ','.join([f"{v.get('license_plate', '---')}/{v.get('id', '')}" for v in vehicles])
        st.session_state["all_vehicles"] = vehicle_list_str
        
    for vehicle in st.session_state.get("all_vehicles", "").split(","):
        vehicle_data = vehicle.split("/")
        if len(vehicle_data) == 2:
            placa, id_vehicle = vehicle_data
            all_vehicles_dict[placa] = id_vehicle

    st.markdown(f"## Relatório para {client_name}")
    st.markdown("#### Selecione os veículos para incluir no relatório:")

    cols_plates = st.columns(2)
    # Cria checkboxes para cada veículo, todos selecionados por padrão
    for i, (placa, id_vehicle) in enumerate(all_vehicles_dict.items()):

        if i % 2 == 0:
            with cols_plates[0]:
                st.checkbox(
                    placa,
                    key=f"vehicle_{id_vehicle}",
                    value=True,
                )
        else:
            with cols_plates[1]:
                st.checkbox(
                    placa,
                    key=f"vehicle_{id_vehicle}",
                    value=True,
                )
    
    st.divider()

    st.markdown("#### Defina os limiares para o relatório:")
    col1, col2, col3 = st.columns(3)
    with col1:
        vel_threshold = st.number_input("Velocidade (km/h)", min_value=0, value=100, key="vel_threshold")
    with col2:
        uppertime_threshold = st.number_input("Hora Máxima (0-23)", min_value=0, max_value=23, value=21, key="uppertime_threshold")
    with col3:
        lowertime_threshold = st.number_input("Hora Mínima (0-23)", min_value=0, max_value=23, value=5, key="lowertime_threshold")

    st.divider()

    if st.button("✅ Gerar Relatório"):
        plates_to_not_do = [
            placa for placa, id_vehicle in all_vehicles_dict.items()
            if not st.session_state.get(f"vehicle_{id_vehicle}")
        ]

        # Monta o dicionário de configuração para a função de processamento
        client_config = {
            'name': client_name,
            'cod': client_id,
            'vel_threshold': vel_threshold,
            'uppertime_threshold': uppertime_threshold,
            'lowertime_threshold': lowertime_threshold,
            'plates_to_not_do': plates_to_not_do
        }

        # Chama a função principal com a configuração montada
        path = process_report(client_config)
        st.info(f"Relatório para {client_name} está sendo processado!")

        if path:
            st.success(f"Relatório para {client_name} gerado com sucesso!")

            with open(path, "rb") as file:
                st.session_state["report_file"] = file.read()

            if st.download_button(
                label="📥 Baixar Relatório",
                data=st.session_state["report_file"],
                file_name=f"relatorio_{client_name}.pdf",
                mime="application/pdf"
            ):
                st.rerun()
                
        else:
            st.error(f"Erro ao gerar relatório para {client_name}.")