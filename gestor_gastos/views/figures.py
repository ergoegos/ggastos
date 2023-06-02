
import plotly.express as px
from services.database import Database
import datetime
import plotly.graph_objects as go
import pandas as pd


class Figures:

    def __init__(self, username: str):

        self.username = username
        self.month_mapping = {
            'January': 'Enero',
            'February': 'Febrero',
            'March': 'Marzo',
            'April': 'Abril',
            'May': 'Mayo',
            'June': 'Junio',
            'July': 'Julio',
            'August': 'Agosto',
            'September': 'Septiembre',
            'October': 'Octubre',
            'November': 'Noviembre',
            'December': 'Diciembre'
        }

    def current_month(self):

        current_date = datetime.datetime.now()
        month_name = current_date.strftime('%B')
        return self.month_mapping.get(month_name)

    def last_month(self):
        current_date = datetime.datetime.now()
        last_month_date = current_date.replace(
            day=1) - datetime.timedelta(days=1)
        last_month_name = last_month_date.strftime('%B')
        return self.month_mapping.get(last_month_name)

    def map_field(self, field, lowercase=False):
        mapping_fields = {"expenses": "Gastos",
                          "incomes": "Ingresos"}
        traduccion = mapping_fields[field]
        if lowercase:
            traduccion = traduccion.lower()
        return traduccion

    def m_exp_total_evolution_line(self):

        with Database() as db:
            df = db.get_table("monthly_expenses", self.username)
            df = df[["month_name", "amount"]]

        fig = px.line(df, x="month_name", y="amount")
        fig.update_layout(
            title="Evolución del gasto mensual",
            width=700,
            height=400,
        )

        fig.update_xaxes(title='', visible=True, showticklabels=True)
        fig.update_yaxes(title='', visible=True, showticklabels=True)
        return fig

    def m_exp_by_concept_total_evolution_bar(self):

        with Database() as db:
            df = db.get_table("monthly_expenses_by_concept", self.username)
            df = df[["month_name", "concept",  "amount"]]

        fig = px.bar(df, x='month_name', y='amount', color='concept')
        fig.update_layout(
            title="Gasto por concepto",
            xaxis_title="",
            yaxis_title="",
            width=750,
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            legend_title_text=""
        )
        fig.update_xaxes(title='', visible=True, showticklabels=True)
        fig.update_yaxes(title='', visible=True, showticklabels=True)

        return fig

    def m_percent_current_pie(self, table: str):
        with Database() as db:
            df = db.get_table(f"monthly_{table}_by_concept", self.username)
            df = df[["month_name", "concept",  "amount"]]
            df = df[df["month_name"] == self.current_month()]
            df = df.assign(percentage=(
                df.amount / df.amount.sum()) * 100).round(2)

        fig = px.pie(df, values='percentage', names='concept',
                     title=f'Distribución porcentual de {self.map_field(table, lowercase=True)} en {self.current_month()}')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=20),
            yaxis=dict(
                tickmode="array",
                titlefont=dict(size=10),
            ),
            autosize=False,
            width=400,
            height=400,
            legend=dict(y=0.50),
            legend_title_text=''
        )
        fig.update_xaxes(title='', visible=True, showticklabels=True)
        fig.update_yaxes(title='', visible=True, showticklabels=True)
        return fig

    def m_percent_evolution_pm_bar_by_concept(self, table: str):
        with Database() as db:
            df = db.get_table(f"monthly_{table}_by_concept", self.username)
            df = df[["month_name", "concept",  "amount"]]
            df = df[(df["month_name"] == self.current_month())
                    | (df["month_name"] == self.last_month())]

        fig = px.bar(df, x="concept", y="amount",
                     color="month_name", barmode="group", title=f"{self.map_field(table)} respecto al mes pasado")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=20),
            yaxis=dict(
                tickmode="array",
                titlefont=dict(size=10),
            ),
            autosize=False,
            width=1000,
            height=400,
            legend=dict(y=0.50),
            legend_title_text=''
        )
        fig.update_xaxes(title='', visible=True, showticklabels=True)
        fig.update_yaxes(title='', visible=True, showticklabels=True)

        return fig

    def m_vs_projection_evolution_line(self, table: str):

        with Database() as db:
            df = db.get_table(f"monthly_{table}", self.username)
            df = df[["month_name", "amount", "amount_expected"]]

        fig = px.line(df, x="month_name", y=["amount", "amount_expected"],
                      title=f"Evolución de {self.map_field(table, lowercase=True)} mensuales respecto a previsión")
        fig.update_traces(name="Total", selector=dict(name="amount"))
        fig.update_traces(name="Total previsto",
                          selector=dict(name="amount_expected"))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=0, t=25, b=0),
            autosize=False,
            width=1500,
            height=300,
            legend=dict(
                y=0.5,
            ), legend_title_text=''
        )
        fig.update_xaxes(title='', visible=True, showticklabels=True)
        fig.update_yaxes(title='', visible=True, showticklabels=True)

        return fig

    def m_inc_total_evolution_line(self):

        with Database() as db:
            df = db.get_table("monthly_incomes", self.username)
            df = df[["month_name", "amount"]]

        fig = px.line(df, x="month_name", y="amount")
        fig.update_layout(
            title="Evolución del ingreso mensual",
            xaxis_title="",
            yaxis_title="",
            width=700,
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
        )
        return fig

    def m_inc_by_concept_total_evolution_bar(self):

        with Database() as db:
            df = db.get_table("monthly_incomes_by_concept", self.username)
            df = df[["month_name", "concept",  "amount"]]

        fig = px.bar(df, x='month_name', y='amount', color='concept')
        fig.update_layout(
            title="Ingresos por concepto",
            xaxis_title="",
            yaxis_title="",
            width=750,
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            legend_title_text=""
        )

        return fig

    def last_month_metric(self, table: str):
        with Database() as db:
            df = db.get_table(f"monthly_{table}", self.username)
            df = df[["month_name", "amount"]]
            df.sort_values(by="month_name", inplace=True, key=lambda x: x.map(
                {v: i for i, v in enumerate(list(self.month_mapping.values()))}))
            df = df[df["month_name"].isin(
                [self.current_month(), self.last_month()])]
            df['percentage_difference'] = df['amount'].pct_change() * 100
            amount, percentage = df[df["month_name"] == self.current_month(
            )][["amount", "percentage_difference"]].values[0]
            return {"label": f"{self.map_field(table)} este mes",
                    "value": amount,
                    "delta":  "{:,.2f} %".format(round(percentage, 2)),
                    "delta_color": "inverse" if table == "expenses" else "normal"}

    def vs_projection_metric(self, table: str):
        with Database() as db:
            df = db.get_table(f"monthly_{table}", self.username)
            df = df[["month_name", "amount", "amount_expected"]]
            df.sort_values(by="month_name", inplace=True, key=lambda x: x.map(
                {v: i for i, v in enumerate(list(self.month_mapping.values()))}))
            df = df[df["month_name"].isin(
                [self.current_month(), self.last_month()])]
            df['difference'] = df['amount'] - df['amount_expected']
            difference = df[df["month_name"] == self.current_month(
            )][["amount", "difference"]].values[0][1]
            return {"label": f"{self.map_field(table)} vs Previsión",
                    "value": "Por debajo" if difference < 0 else "Por encima",
                    "delta": "{:,.2f} €".format(round(difference, 2)),
                    "delta_color": "inverse" if table == "expenses" else "normal"}

    def max_source(self, table: str):
        with Database() as db:
            df = db.get_table(f"monthly_{table}_by_concept", self.username)
            df = df[["month_name", "concept",  "amount"]]
            df2 = df[df["month_name"] == self.current_month()]
            grouped_df = df2.groupby("concept").sum()
            max_amount_concept = grouped_df["amount"].idxmax()
            previous_month_amount = float(df.loc[(df["concept"] == max_amount_concept) & (
                df["month_name"] == self.last_month()), "amount"])
            delta = previous_month_amount - \
                grouped_df.loc[max_amount_concept, "amount"]
            field = self.map_field(table, lowercase=True)[:-1]
            return {"label": f"Principal {field} ",
                    "value": max_amount_concept,
                    "delta": "{:,.2f} €".format(round(delta, 2)),
                    }

    def savings_evolution_line(self):

        with Database() as db:
            df = db.get_table("monthly_savings", self.username)
            df = df[["month_name", "ahorro_mensual", "ahorro_esperado"]]

        fig = px.line(df, x="month_name", y=["ahorro_mensual", "ahorro_esperado"])
        fig.update_traces(name="Ahorro total",
                          selector=dict(name="ahorro_mensual"))
        fig.update_traces(name="Ahorro previsto",
                          selector=dict(name="ahorro_esperado"))

        fig.update_layout(
            title="Evolución del ahorro mensual",
            xaxis_title="",
            yaxis_title="",
            width=1500,
            height=300,
            legend=dict(y=0.50),
            legend_title_text=''
        )
        return fig

    def expense_vs_income(self):

        with Database() as db:
            df = db.get_table("monthly_savings", self.username)
            df = df[["month_name", "gastos_mensuales", "ingresos_mensuales"]]
            df["gastos_mensuales"] = df["gastos_mensuales"] * -1

            fig = go.Figure()
            fig.add_trace(go.Bar(x=df["month_name"], y=df["ingresos_mensuales"],
                                 base=[-500, -600, -700],

                                 name='Gastos'))
            fig.add_trace(go.Bar(x=df["month_name"], y=df["gastos_mensuales"],
                                 base=0,

                                 name='Ingresos'
                                 ))

            fig.update_layout(
                margin=dict(l=20, r=0, t=20, b=0),
                width=900,
                height=400,
                legend=dict(
                    y=0.5,
                ),
            )

            return fig

    def progress_saving_projection(self):
        with Database() as db:
            df = db.get_table("monthly_savings", self.username)
            print(df)
            df = df[["month_name", "ahorro_mensual", "ahorro_esperado"]]
            df['porcentaje_ahorro'] = (
                df['ahorro_mensual'] / df['ahorro_esperado']) * 100
            porcentaje = df[df["month_name"] == self.current_month()][[
                "porcentaje_ahorro"]].values[0][0]

        if porcentaje > 100:
            porcentaje = 100

        df = pd.DataFrame({'names': ['progress', ''],
                           'values': [100 - porcentaje, porcentaje]})

        fig = px.pie(df, values='values', names='names', hole=0.5,
                     color_discrete_sequence=['rgb(133, 200, 255)', 'rgba(0,0,0,0)'], title="Objetivo de ahorro mensual")

        fig.data[0].textfont.color = 'white'
        fig.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            width=500,
            height=400,
            showlegend=False
        )
        return fig
