import os
import csv
from datetime import datetime

from kivy.config import Config
Config.set('graphics', 'resizable', True)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE
    ])

CAMINHO_DOWNLOAD_ANDROID = "/sdcard/Download"
NOME_ARQUIVO = "historico_uber.csv"

if os.path.exists(CAMINHO_DOWNLOAD_ANDROID):
    CAMINHO_FINAL_CSV = os.path.join(CAMINHO_DOWNLOAD_ANDROID, NOME_ARQUIVO)
else:
    CAMINHO_FINAL_CSV = NOME_ARQUIVO

CABECALHO_CSV = [
    "Data", "Motorista", "KM_Inicial", "KM_Final", "Distancia_KM",
    "Faturamento_Bruto", "Gasto_Combustivel", "Custo_Fixo",
    "Custo_Total", "Lucro_Total", "Lucro_Voce", "Lucro_Amigo"
]

def limpar_numero_csv(texto):
    try:
        return float(texto.replace(',', '.'))
    except ValueError:
        return 0.0

def formatar_numero_br(valor):
    return f"{valor:.2f}".replace('.', ',')

class MenuInicialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        titulo = Label(
            text="--- CALCULADORA UBER COMPARTILHADA ---\nMaringá - PR",
            font_size='20sp',
            bold=True,
            halign='center',
            size_hint_y=0.2
        )
        layout.add(titulo)
        btn_calcular = Button(text="Calcular Novo Turno", font_size='16sp', size_hint_y=0.2)
        btn_calcular.bind(on_press=self.ir_para_calculo)
        btn_geral = Button(text="Relatório de Fechamento Geral", font_size='16sp', size_hint_y=0.2)
        btn_geral.bind(on_press=self.ir_para_geral)
        btn_mensal = Button(text="Relatório Mensal Filtrado", font_size='16sp', size_hint_y=0.2)
        btn_mensal.bind(on_press=self.ir_para_mensal)
        layout.add(btn_calcular)
        layout.add(btn_geral)
        layout.add(btn_mensal)
        rodape = Label(text="Controle de Frota Compartilhada v1.0", font_size='12sp', size_hint_y=0.1)
        layout.add(rodape)
        self.add_widget(layout)

    def ir_para_calculo(self, instance):
        self.manager.current = 'calcular_turno'
    def ir_para_geral(self, instance):
        self.manager.get_screen('relatorio_geral').carregar_dados_gerais()
        self.manager.current = 'relatorio_geral'
    def ir_para_mensal(self, instance):
        self.manager.current = 'relatorio_mensal'

class CalcularTurnoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout_principal = BoxLayout(orientation='vertical', padding=15, spacing=10)
        btn_voltar = Button(text="<- Voltar ao Menu", size_hint_y=None, height='45dp')
        btn_voltar.bind(on_press=self.voltar_menu)
        layout_principal.add(btn_voltar)
        scroll_form = ScrollView()
        form_grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        form_grid.bind(minimum_height=form_grid.setter('height'))
        form_grid.add(Label(text="Quem dirigiu o carro neste turno?", bold=True, size_hint_y=None, height='30dp'))
        box_paulo = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.check_paulo = CheckBox(group='motorista', active=True)
        self.check_paulo.bind(active=self.on_checkbox_active)
        box_paulo.add(self.check_paulo)
        box_paulo.add(Label(text="Você (Paulo) / Principal"))
        form_grid.add(box_paulo)
        box_pedro = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.check_pedro = CheckBox(group='motorista')
        self.check_pedro.bind(active=self.on_checkbox_active)
        box_pedro.add(self.check_pedro)
        box_pedro.add(Label(text="Seu Amigo (Pedro) / Secundário"))
        form_grid.add(box_pedro)
        form_grid.add(Label(text="KM Inicial:", size_hint_y=None, height='25dp'))
        self.input_km_ini = TextInput(multiline=False, input_filter='float', size_hint_y=None, height='40dp')
        self.input_km_ini.bind(text=self.feedback_km_inicial)
        form_grid.add(self.input_km_ini)
        form_grid.add(Label(text="KM Final:", size_hint_y=None, height='25dp'))
        self.input_km_fim = TextInput(multiline=False, input_filter='float', size_hint_y=None, height='40dp')
        self.input_km_fim.bind(text=self.feedback_km_final)
        form_grid.add(self.input_km_fim)
        form_grid.add(Label(text="Total Faturado no App Uber (R$):", size_hint_y=None, height='25dp'))
        self.input_faturamento = TextInput(multiline=False, input_filter='float', size_hint_y=None, height='40dp')
        self.input_faturamento.bind(text=self.feedback_faturamento)
        form_grid.add(self.input_faturamento)
        form_grid.add(Label(text="Preço do Litro do Combustível (R$):", size_hint_y=None, height='25dp'))
        self.input_combustivel = TextInput(multiline=False, input_filter='float', size_hint_y=None, height='40dp')
        self.input_combustivel.bind(text=self.feedback_combustivel)
        form_grid.add(self.input_combustivel)
        form_grid.add(Label(text="Média de Consumo do Carro (km/L):", size_hint_y=None, height='25dp'))
        self.input_consumo = TextInput(multiline=False, input_filter='float', size_hint_y=None, height='40dp')
        self.input_consumo.bind(text=self.feedback_consumo)
        form_grid.add(self.input_consumo)
        scroll_form.add_widget(form_grid)
        layout_principal.add(scroll_form)
        self.label_feedback = Label(
            text="Aguardando preenchimento dos dados...\n",
            size_hint_y=None,
            height='80dp',
            halign='center',
            color=(0.2, 0.8, 0.2, 1)
        )
        layout_principal.add(self.label_feedback)
        btn_salvar = Button(text="Calcular & Salvar Turno", size_hint_y=None, height='50dp', background_color=(0, 0.6, 0, 1))
        btn_salvar.bind(on_press=self.processar_e_salvar)
        layout_principal.add(btn_salvar)
        self.add_widget(layout_principal)

    def on_checkbox_active(self, checkbox, value):
        if value:
            motorista = "Você (Paulo)" if checkbox == self.check_paulo else "Seu Amigo (Pedro)"
            self.label_feedback.text = f"-> Motorista selecionado:\n{motorista}\n"
    def feedback_km_inicial(self, instance, value):
        if value: self.label_feedback.text = f"-> Métrica registrada:\n{value} km iniciais.\n"
    def feedback_km_final(self, instance, value):
        if value: self.label_feedback.text = f"-> Métrica registrada:\n{value} km finais.\n"
    def feedback_faturamento(self, instance, value):
        if value: self.label_feedback.text = f"-> Financeiro registrado:\nR$ {value} faturados.\n"
    def feedback_combustivel(self, instance, value):
        if value: self.label_feedback.text = f"-> Combustível registrado:\nR$ {value} por litro.\n"
    def feedback_consumo(self, instance, value):
        if value: self.label_feedback.text = f"-> Consumo registrado:\n{value} km/L de média.\n"
    def voltar_menu(self, instance):
        self.manager.current = 'menu_inicial'

    def processar_e_salvar(self, instance):
        try:
            motorista_atual = "Voce" if self.check_paulo.active else "Amigo"
            km_inicial = float(self.input_km_ini.text or 0)
            km_final = float(self.input_km_fim.text or 0)
            faturamento_bruto = float(self.input_faturamento.text or 0)
            valor_combustivel = float(self.input_combustivel.text or 0)
            eficiencia_veiculo = float(self.input_consumo.text or 1)
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            delta_deslocamento = km_final - km_inicial
            if delta_deslocamento <= 0:
                self.label_feedback.text = "[ERRO] Quilometragem final deve\nser maior que a inicial!"
                return
            litros_consumidos = delta_deslocamento / eficiencia_veiculo
            gasto_combustivel = litros_consumidos * valor_combustivel
            custo_fixo_diario = 47.73
            custo_total_dia = gasto_combustivel + custo_fixo_diario
            lucro_liquido_total = faturamento_bruto - custo_total_dia
            if motorista_atual == "Amigo":
                lucro_parceiro = lucro_liquido_total
                lucro_seu = 0.0
            else:
                lucro_parceiro = 0.0
                lucro_seu = lucro_liquido_total
            arquivo_existe = os.path.exists(CAMINHO_FINAL_CSV)
            dados_dia = [
                data_hoje, motorista_atual, km_inicial, km_final, delta_deslocamento,
                faturamento_bruto, gasto_combustivel, custo_fixo_diario, custo_total_dia,
                lucro_liquido_total, lucro_seu, lucro_parceiro
            ]
            dados_formatados = [data_hoje, motorista_atual] + [formatar_numero_br(x) for x in dados_dia[2:]]
            diretorio_destino = os.path.dirname(CAMINHO_FINAL_CSV)
            if diretorio_destino and not os.path.exists(diretorio_destino):
                os.makedirs(diretorio_destino, exist_ok=True)
            with open(CAMINHO_FINAL_CSV, mode='a', newline='', encoding='utf-8') as arquivo:
                escritor = csv.writer(arquivo, delimiter=';')
                if not arquivo_existe:
                    escritor.writerow(CABECALHO_CSV)
                escritor.writerow(dados_formatados)
            self.label_feedback.text = "[OK] Turno salvo com sucesso\naqui em Maringá!"
            self.input_km_ini.text = ""
            self.input_km_fim.text = ""
            self.input_faturamento.text = ""
            self.input_combustivel.text = ""
            self.input_consumo.text = ""
        except Exception as e:
            self.label_feedback.text = f"[!] Erro ao salvar dados:\n{str(e)}"

class RelatorioGeralScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        btn_voltar = Button(text="<- Voltar ao Menu", size_hint_y=None, height='45dp')
        btn_voltar.bind(on_press=self.voltar_menu)
        layout.add(btn_voltar)
        layout.add(Label(text="FECHAMENTO HISTÓRICO GERAL", bold=True, size_hint_y=None, height='30dp'))
        self.scroll = ScrollView()
        self.label_dados = Label(text="", font_size='14sp', size_hint_y=None, halign='left', valign='top')
        self.label_dados.bind(texture_size=self.label_dados.setter('size'))
        self.scroll.add_widget(self.label_dados)
        layout.add(self.scroll)
        self.add_widget(layout)
    def voltar_menu(self, instance):
        self.manager.current = 'menu_inicial'
    def carregar_dados_gerais(self):
        if not os.path.exists(CAMINHO_FINAL_CSV):
            self.label_dados.text = "Nenhum dado registrado ainda!\n\nO arquivo 'historico_uber.csv' não foi localizado."
            return
        total_km = 0.0
        total_faturamento = 0.0
        total_combustivel = 0.0
        total_custo_fixo = 0.0
        total_lucro_voce = 0.0
        total_lucro_amigo = 0.0
        corridas_voce = 0
        corridas_amigo = 0
        try:
            with open(CAMINHO_FINAL_CSV, mode='r', encoding='utf-8') as arquivo:
                leitor = csv.reader(arquivo, delimiter=';')
                next(leitor)
                for linha in leitor:
                    if not linha: continue
                    motorista = linha[1]
                    total_km += limpar_numero_csv(linha[4])
                    total_faturamento += limpar_numero_csv(linha[5])
                    total_combustivel += limpar_numero_csv(linha[6])
                    total_custo_fixo += limpar_numero_csv(linha[7])
                    total_lucro_voce += limpar_numero_csv(linha[10])
                    total_lucro_amigo += limpar_numero_csv(linha[11])
                    if motorista == "Voce": corridas_voce += 1
                    else: corridas_amigo += 1
            relatorio = (
                f"========================================\n"
                f"         ACUMULADO DO PERÍODO           \n"
                f"========================================\n"
                f"Total de Dias Rodados : {corridas_voce + corridas_amigo} dias\n"
                f" -> Seus turnos (Paulo)  : {corridas_voce} dias\n"
                f" -> Turnos do Amigo (Pedro): {corridas_amigo} dias\n"
                f"Distância Total       : {total_km:.2f} km\n"
                f"----------------------------------------\n"
                f"Faturamento Bruto     : R$ {total_faturamento:.2f}\n"
                f"Gasto com Combustível : R$ {total_combustivel:.2f}\n"
                f"Fundo de Custos Fixos : R$ {total_custo_fixo:.2f} (Carro)\n"
                f"----------------------------------------\n"
                f"SEU LUCRO LÍQUIDO (Paulo): R$ {total_lucro_voce:.2f} 💰\n"
                f"LUCRO DO AMIGO (Pedro)   : R$ {total_lucro_amigo:.2f} 🤝\n"
                f"========================================"
            )
            self.label_dados.text = relatorio
        except Exception as e:
            self.label_dados.text = f"Erro ao ler histórico de dados:\n{str(e)}"

class RelatorioMensalScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        btn_voltar = Button(text="<- Voltar ao Menu", size_hint_y=None, height='45dp')
        btn_voltar.bind(on_press=self.voltar_menu)
        layout.add(btn_voltar)
        layout.add(Label(text="FECHAMENTO MENSAL FILTRADO", bold=True, size_hint_y=None, height='30dp'))
        layout_busca = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp', spacing=10)
        layout_busca.add(Label(text="MM/AAAA:", size_hint_y=None, height='45dp', size_hint_x=0.3))
        self.input_filtro = TextInput(text="06/2026", multiline=False, size_hint_x=0.4)
        btn_buscar = Button(text="Filtrar", size_hint_x=0.3)
        btn_buscar.bind(on_press=self.executar_filtro_mensal)
        layout_busca.add(self.input_filtro)
        layout_busca.add(btn_buscar)
        layout.add(layout_busca)
        self.scroll = ScrollView()
        self.label_dados = Label(text="Digite o mês/ano acima e clique em Filtrar.", font_size='14sp', size_hint_y=None, halign='left', valign='top')
        self.label_dados.bind(texture_size=self.label_dados.setter('size'))
        self.scroll.add_widget(self.label_dados)
        layout.add(self.scroll)
        self.add_widget(layout)
    def voltar_menu(self, instance):
        self.manager.current = 'menu_inicial'
    def ejecutar_filtro_mensal(self, instance):
        mes_filtro = self.input_filtro.text.strip()
        if not mes_filtro:
            self.label_dados.text = "Por favor, insira um filtro válido."
            return
        if not os.path.exists(CAMINHO_FINAL_CSV):
            self.label_dados.text = "Nenhum dado registrado ainda!"
            return
        total_km, total_faturamento, total_combustivel, total_custo_fixo, total_lucro_voce, total_lucro_amigo = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        corridas_voce, corridas_amigo = 0, 0
        dados_encontrados = False
        try:
            with open(CAMINHO_FINAL_CSV, mode='r', encoding='utf-8') as arquivo:
                leitor = csv.reader(arquivo, delimiter=';')
                next(leitor)
                for linha in leitor:
                    if not linha: continue
                    data_corrida = linha[0]
                    if mes_filtro in data_corrida:
                        dados_encontrados = True
                        motorista = linha[1]
                        total_km += limpar_numero_csv(linha[4])
                        total_faturamento += limpar_numero_csv(linha[5])
                        total_combustivel += limpar_numero_csv(linha[6])
                        total_custo_fixo += limpar_numero_csv(linha[7])
                        total_lucro_voce += limpar_numero_csv(linha[10])
                        total_lucro_amigo += limpar_numero_csv(linha[11])
                        if motorista == "Voce": corridas_voce += 1
                        else: corridas_amigo += 1
            if not dados_encontrados:
                self.label_dados.text = f"[!] Nenhum registro encontrado para {mes_filtro}."
            else:
                relatorio = (
                    f"========================================\n"
                    f"         ACUMULADO DE: {mes_filtro}      \n"
                    f"========================================\n"
                    f"Total de Dias Rodados : {corridas_voce + corridas_amigo} dias\n"
                    f" -> Seus turnos (Paulo)  : {corridas_voce} dias\n"
                    f" -> Turnos do Amigo (Pedro): {corridas_amigo} dias\n"
                    f"Distância Total       : {total_km:.2f} km\n"
                    f"----------------------------------------\n"
                    f"Faturamento Bruto     : R$ {total_faturamento:.2f}\n"
                    f"Gasto com Combustível : R$ {total_combustivel:.2f}\n"
                    f"Fundo de Custos Fixos : R$ {total_custo_fixo:.2f} (Carro)\n"
                    f"----------------------------------------\n"
                    f"SEU LUCRO LÍQUIDO (Paulo): R$ {total_lucro_voce:.2f} 💰\n"
                    f"LUCRO DO AMIGO (Pedro)   : R$ {total_lucro_amigo:.2f} 🤝\n"
                    f"========================================"
                )
                self.label_dados.text = relatorio
        except Exception as e:
            self.label_dados.text = f"Erro ao filtrar dados: {str(e)}"

class UberCalculatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuInicialScreen(name='menu_inicial'))
        sm.add_widget(CalcularTurnoScreen(name='calcular_turno'))
        sm.add_widget(RelatorioGeralScreen(name='relatorio_geral'))
        sm.add_widget(RelatorioMensalScreen(name='relatorio_mensal'))
        return sm

if __name__ == '__main__':
    UberCalculatorApp().run()
