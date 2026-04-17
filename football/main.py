import panel as pn
from dashboard import create_dashboard

dashboard = create_dashboard()
dashboard.servable()

if __name__ == "__main__":
    pn.serve(dashboard, show=True)