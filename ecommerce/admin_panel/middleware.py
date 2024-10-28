from .models import UserEventTracking
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from ipaddress import ip_address, ip_network
from geoip2.errors import AddressNotFoundError


class UserEventTrackingMiddleware:
    """Middleware to track user events"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip certain requests
        if self.should_skip_request(request):
            return self.get_response(request)

        # Capture the response from the view
        response = self.get_response(request)

        # Ensure the session has a key
        if not request.session.session_key:
            request.session.save()
        session_id = request.session.session_key

        # Capture event details
        event_type = self.get_event_type(request)
        event_metadata = self.get_event_metadata(request)
        client_ip = self.get_client_ip(request)
        device_type = self.get_device_type(request)
        browser_info = request.META.get("HTTP_USER_AGENT", "")

        # Determine location based on the client's IP address
        if self.is_private_ip(client_ip):
            location = "Local Network"
        else:
            location = self.get_location_from_ip(client_ip)

        object_info = None

        if event_metadata.get("product_id"):
            object_info = event_metadata.get("product_id")
        if event_metadata.get("category_name"):
            object_info = event_metadata.get("category_name")
        if event_metadata.get("search_term"):
            object_info = event_metadata.get("search_term")

        # Log the event based on user authentication status
        event_data = {
            "requested_url": request.build_absolute_uri(),
            "event_type": event_type,
            "event_metadata": event_metadata,
            "session_id": session_id,
            "ip_address": client_ip,
            "device_type": device_type,
            "browser_info": browser_info,
            "location": location,
            "object_info": object_info,  # Store serialized object_info
            "user": None,
        }

        if request.user.is_authenticated:
            event_data["user"] = request.user

        UserEventTracking.objects.create(**event_data)

        return response

    @staticmethod
    def get_event_type(request):
        """Determine the type of event based on the request and action taken."""

        # Check if the request is related to a product detail page
        if "/product-details/" in request.path and request.method == "GET":
            return "product_view"

        # Check if the user is adding a product to their cart
        if "add-cart" in request.path and request.method == "POST":
            return "add_to_cart"

        # Check if the user is adding a product to their wishlist
        if "/add-wishlist/" in request.path and request.method == "POST":
            return "add_to_wishlist"

        # Other events
        if request.path == "/login/":
            return "login"
        elif request.path == "/logout/":
            return "logout"
        elif request.method == "POST":
            return "form_submission"

        return "page_view"

    @staticmethod
    def get_event_metadata(request):
        """Extract additional metadata from the request, including product and user-related details."""

        metadata = {
            "path": request.path,
            "method": request.method,
            "GET_params": request.GET.dict(),
            "POST_data": request.POST.dict() if request.method == "POST" else None,
        }

        # Example of capturing product-related metadata

        if request.path.startswith("/product-details/"):
            # Extract product_id from the URL using URL parameters
            product_id = request.resolver_match.kwargs.get(
                "id", None
            )  # Get the product ID from the
            metadata["product_id"] = product_id

        # Example of capturing category or filter-related metadata
        if "/products/" in request.path:
            if request.GET.dict().get("cat"):
                metadata["category_name"] = request.GET.dict().get("cat", None)

        # Capturing search-related metadata
        search_term = request.GET.get("search", None)
        if search_term:
            metadata["search_term"] = search_term

        # Capture user info if logged in
        if request.user.is_authenticated:
            metadata["user_id"] = request.user.id

        return metadata

    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address from the request."""

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def get_device_type(request):
        """Determine the type of device from the user agent."""

        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        if "mobile" in user_agent:
            return "mobile"
        if "tablet" in user_agent:
            return "tablet"
        return "desktop"

    @staticmethod
    def is_private_ip(ip):
        """Check if an IP address is private (including 127.0.0.1)."""

        private_networks = [
            ip_network("127.0.0.0/8"),
            ip_network("10.0.0.0/8"),
            ip_network("172.16.0.0/12"),
            ip_network("192.168.0.0/16"),
        ]
        ip_addr = ip_address(ip)
        return any(ip_addr in network for network in private_networks)

    @staticmethod
    def get_location_from_ip(ip_address):
        """Fetch location data using GeoIP2, or return 'Unknown Location' if not found."""

        geoip = GeoIP2()
        try:
            geoip_response = geoip.city(ip_address)
            continent_name = geoip_response.get("continent_name", "")
            country = geoip_response.get("country_name", "")
            return f"continent_name = {continent_name}, country = {country}".strip(", ")
        except AddressNotFoundError:
            return "Unknown Location"

    def should_skip_request(self, request):
        """Determine if the request should be skipped for tracking."""

        if request.path.startswith("/static/"):
            return True
        if request.path.startswith("/admin/"):
            return True
        if request.path.startswith("/admin-panel/"):
            return True
        if request.path.startswith("/media/"):
            return True
        if request.path.startswith("/__debug__/"):
            return True
        if request.path == "/health-check/":
            return True
        return False
