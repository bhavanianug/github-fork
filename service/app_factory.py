from service.singleton import singleton
from config.enums import FlaskOAuthServerConfig
from config.config import oauthserverconfig
from flask_oauthlib.client import OAuth
from service.oauthapp import OAuthApp
from requests.exceptions import HTTPError
from http import HTTPStatus


#
@singleton
class GithubOAuthApp(OAuthApp):
    """Singleton Github OAuth Flask App class.
    This class contains the underlying OAuthRemoteApp object
    """
    appconfig = oauthserverconfig.get('github')

    def __init__(self, logger):
        self.logger = logger
        # self.create_oauth_app()

    def create_oauth_app(self):
        """Create the OAuthRemoteApp object using the oauthlib library

        :return: None
        """
        try:
            oauth = OAuth()
            self.oauthapp = oauth.remote_app(
                'github',
                consumer_key=self.appconfig.get(FlaskOAuthServerConfig.CLIENT_ID),
                consumer_secret=self.appconfig.get(FlaskOAuthServerConfig.CLIENT_SECRET),
                request_token_params=self.appconfig.get(FlaskOAuthServerConfig.REQUEST_TOKEN),
                base_url=self.appconfig.get(FlaskOAuthServerConfig.BASE_URL),
                request_token_url=None,
                access_token_method=self.appconfig.get(FlaskOAuthServerConfig.ACCESS_TOKEN_METHOD),
                access_token_url=self.appconfig.get(FlaskOAuthServerConfig.ACCESS_TOKEN_URL),
                authorize_url=self.appconfig.get(FlaskOAuthServerConfig.AUTH_URL),
            )
        except Exception as exc:
            if self.logger:
                self.logger.exception('create_oauth_app : Exception creating the OAuth App {}'
                                      .format(exc))
            raise

    def _logmessage(self, message, exc):
        """Helper method to log exceptions

        :param message: Input string message
        :param exc: Exception to be logged
        :return: None
        """
        if self.logger:
            self.logger.exception(
                'handleoauthlogin : {} {}'.format(message, exc))

    def handle_oauth_login(self):
        """Handle OAuth login into the host server(github, facebook, etc)

        :return: str message
        """
        try:
            resp = self.oauthapp.get('/user')
            if resp.status == HTTPStatus.OK:
                self.logger.info('handleoauthlogin :Logged in as id={} name={} '.\
                                 format(resp.data.get('id'), resp.data.get('login')))
                return resp.status
        except HTTPError as http_err:
            self._logmessage('handleoauthlogin : HTTP Error occurred in a Github GET request'\
                             , http_err)
            raise
        except Exception as exc:
            self._logmessage('handleoauthlogin : Exception when getting User details from GitHub'\
                             , exc)
            raise

    def create_fork(self, request):
        """Create a fork for repository name and owner contained in the request parameters

        :param request: POST request parameters
        :return: str message
        """
        try:
            repoowner = request.args.get('repoowner')
            reponame = request.args.get('reponame')
            if repoowner and reponame:
                self.logger.info('create fork repoowner {} repo name {} '.format(repoowner, reponame))
                resp = self.oauthapp.post('/repos/' + repoowner + '/' + reponame + '/forks',\
                                          content_type='application/json')
                if resp.status == HTTPStatus.ACCEPTED:
                    self.logger.info('create_fork data {} {}'.\
                                     format(resp.data.get('full_name'), resp.status))
                    return resp.status
                else:
                    self.logger.info('Check Repository Name or Owner Name'.\
                                     format(resp.data))
                    raise ValueError('Check Repository Name or Owner Name'.format(resp.data))
            else:
                self.logger.info('Missing Repository Name {} or Owner Name {}'.\
                                 format(reponame, repoowner))
                raise ValueError('Missing Repository Name {} or Owner Name {}'.\
                                 format(reponame, repoowner))
        except Exception as exc:
            self._logmessage('handleoauthlogin : Exception when getting User details from GitHub'
                             , exc)
            raise


@singleton
class FacebookOAuthApp(OAuthApp):
    pass


@singleton
class TwitterOAuthApp(OAuthApp):
    pass
