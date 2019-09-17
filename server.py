import cachetools
import falcon
import pytube
import config
import framework
from falcon_cors import CORS
from wsgiref.simple_server import make_server
from gevent.pywsgi import WSGIServer
from pytube.extract import watch_url
from pytube.helpers import safe_filename


# Best soundtrack: BJhF0L7pfo8
video_cache = cachetools.LFUCache(maxsize=config.CACHE_SIZE)


class Track:
    @staticmethod
    def on_get(request, response):
        variables = {}
        video_id = request.get_param("id", required=True, store=variables)
        _type = request.get_param("type", required=False, store=variables, default="audio")
        _format = request.get_param("format", required=False, store=variables, default="mp4")
        # TODO: Handle quality filtering
        # quality = request.get_param_as_int("quality", required=False, store=variables, default="128")

        # TODO: Properly handle validation and API errors
        if _type not in ("video", "audio"):
            raise falcon.HTTPInvalidParam(param_name="type", msg="")
        if _format not in ("mp3", "mp4", "3gpp", "webm"):
            raise falcon.HTTPInvalidParam(param_name="format", msg="")

        if video_id in video_cache:
            video = video_cache[video_id]
        else:
            video = pytube.YouTube(watch_url(video_id))
            video_cache[video_id] = video

        stream = video.streams.filter(type=_type, subtype=_format).first()
        if stream is None:
            raise falcon.HTTPBadRequest()

        try:
            filename = video.player_config_args["player_response"]["videoDetails"]["title"]
        except KeyError:
            filename = video_id
        filename = safe_filename(filename, max_length=25)

        # Handle stream download manually
        response.downloadable_as = f"{filename}.{_format}"
        response.content_type = stream.mime_type
        response.content_length = stream.filesize
        response.stream = stream.stream_to_buffer()

    # TODO: Add preflight to obtain possible qualities and formats?


def base_error_handler(error, request, response, params):
    response.status = falcon.HTTP_500
    response.json = {"error": config.HTTP_ERROR_MESSAGE[response.status_code],
                     "description": error.description if hasattr(error, "description") else
                     config.HTTP_ERROR_MESSAGE[response.status_code].replace("_", " ").capitalize()}


def http_error_handler(error, request, response, params):
    response.status = error.status
    base_error_handler(error, request, response, params)


application = falcon.API(
    middleware=[
        CORS(
            allow_all_origins=True,
            allow_all_headers=False,
            allow_headers_list=["Origin", "Accept", "Content-Type", "X-Requested-With", "X-CSRF-Token"],
            allow_all_methods=True,
            max_age=86400,
        ).middleware
    ],
    response_type=framework.Response)
application.req_options.auto_parse_form_urlencoded = True
application.add_error_handler(Exception, base_error_handler)
application.add_error_handler(falcon.HTTPError, http_error_handler)
application.add_error_handler(falcon.HTTPStatus, application._http_status_handler)
application.add_route("/track", Track())

server = (WSGIServer if config.HTTP_ASYNC else make_server)(
    host=config.HTTP_HOST, port=config.HTTP_PORT, app=application
)
server.serve_forever()
