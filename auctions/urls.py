from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from django.views.generic.base import TemplateView


urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("listings", views.listings, name="listings"),
    path("delete_listing/<int:listing_id>",
         views.delete_listing, name="delete_listing"),
    path("edit_listing/<int:listing_id>",
         views.edit_listing, name="edit_listing"),
    path("import_csv", views.import_csv, name="import_csv"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user_profile/<int:user_id>", views.user_profile, name="user_profile"),
    path("create", views.create, name="create"),
    path("edit_listing/<int:listing_id>",
         views.edit_listing, name="edit_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("import_csv", views.import_csv, name="import_csv"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.categories, name="categories"),
    path("create_category", views.create_category, name="create_category"),
    path("auction/listing/<int:listing_id>/comment",
         views.comment, name="comment"),
    path("auction/listing/<int:listing_id>/bid", views.bid, name="bid"),
    path("auction/listing/<int:listing_id>/close_listing",
         views.close_listing, name="close_listing"),
    path("auction/watchlist", views.watchlist, name="watchlist"),
    path("auction/watchlist/<int:listing_id>/update/<str:reverse_method>",
         views.update_watchlist, name="update_watchlist"),
    path("profits", views.profits, name="profits"),
    path("expenses", views.expenses, name="expenses"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
