from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns

from . import views

app_name = "auctions"

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
    path("auction/create", views.create, name="create"),
    path("edit_listing/<int:listing_id>",
         views.edit_listing, name="edit_listing"),
    path("auction/listing/<int:listing_id>", views.listing, name="listing"),
    path("import_csv", views.import_csv, name="import_csv"),
    path("auction/categories", views.categories, name="categories"),
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
    path('filter/', views.filter, name="filter"),
    path('like/<int:pk>', views.like, name='like_listing'),
    path('rate_listing', views.rate_listing, name='rate_listing'),
    path('charge/', views.charge, name='charge'),
    path('update_userInfo/<int:user_id>',
         views.update_userInfo, name='update_userInfo'),
    path('support/', views.support, name='support'),
    path('agreement/', views.agreement, name='agreement'),
    path('privacy/', views.privacy, name='privacy'),
    path('shipping/', views.shipping, name='shipping'),
    path('accounts/login/', views.login_view, name='login'),

    # Password reset Views
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="auctions/password_reset.html",
         html_email_template_name='auctions/password_reset_email.html'), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="auctions/password_reset_sent.html"),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="auctions/password_reset_form.html"),
         name="password_reset_confirm"),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="auctions/password_reset_done.html"), name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
