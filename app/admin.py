from fastapi import FastAPI

from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.views import CustomView

from config import settings
from .db import engine
from .models import TokenEvent


def setup_admin(app: FastAPI) -> None:
    admin = Admin(
        engine,
        title=settings.admin_title,
        base_url="/admin",
        route_name="admin",
        statics_dir="app/admin/static",
        templates_dir="app/admin/templates",
        index_view=CustomView(
            label="Dashboard",
            icon="fa fa-chart-line",
            path="/",
            template_path="dashboard.html",
            add_to_menu=False,
        ),
    )

    admin.add_view(ModelView(TokenEvent))
    admin.mount_to(app)
