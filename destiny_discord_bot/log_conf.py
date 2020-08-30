import json
import logging
import logging.config
import os

_HERE = os.path.dirname(__file__)


def _isfile(*parts):
    return os.path.isfile(os.path.join(*parts))


def _trace_to_root(start=_HERE):
    """Yield directories from `start` parent to its root path"""
    parts = start.split(os.sep)
    while parts:
        yield os.sep.join(parts)
        parts.pop()


def _resolve_project_path():
    """
    Find the path to the project this file resides in; defaults to this
    file's parent if no project found.
    """
    trace = _trace_to_root()
    try:
        path = next(p for p in trace if not _isfile(p, '__init__.py'))
    except StopIteration:
        path = _HERE
    return path


def _resolve_package_path():
    """
    Find the path to the package this file resides in; defaults to this
    file's parent if no package found.
    """
    project = _resolve_project_path()
    rel_path = os.path.relpath(_HERE, project)
    head = rel_path.split(os.sep)[0]
    return _HERE if head == '.' else os.path.join(project, head)


def _resolve_config_path(cfg_file):
    for curr in _trace_to_root():
        if _isfile(curr, cfg_file):
            return os.path.join(curr, cfg_file)
    raise FileNotFoundError(cfg_file)


class _LoggingConfig:

    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = object.__new__(cls)
        return cls._singleton

    def __init__(self, config='logging.json'):
        self.project = _resolve_project_path()
        self.package = _resolve_package_path()
        with open(_resolve_config_path(config)) as f:
            self._cfg = json.load(f)
        self.configure()

    def _replace_tag(self, string, tag='<package>'):
        """Replace instances of `tag` with the local package's name"""
        basename = os.path.basename(self.package)
        return string.replace(tag, basename)

    def _configure_handler_file_names(self):
        """Replace filename tags with this package's name"""
        log_dir = os.path.join(self.project, self._cfg['log_directory'])
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)

        for handler in self._cfg['handlers'].values():
            try:
                name = self._replace_tag(handler['filename'])
            except KeyError:
                continue
            else:
                handler['filename'] = os.path.join(log_dir, name)

    def _configure_logger_names(self):
        """Sub out tags in logger names with the local package name"""
        for name in self._cfg['loggers']:
            logger = self._cfg['loggers'].pop(name)
            subbed = self._replace_tag(name)
            self._cfg['loggers'][subbed] = logger

    def configure(self):
        """
        Run local configurations before passing internal config dict to the
        default logging *Configurator.
        """
        self._configure_handler_file_names()
        self._configure_logger_names()
        logging.config.dictConfig(self._cfg)

    @classmethod
    def get_logger(cls, name):
        self = cls()

        file = name.replace('.', os.sep) + '.py'
        if _isfile(self.package, file):
            base = os.path.basename(self.package)
            name = '{}.{}'.format(base, name)
        return logging.getLogger(name)


get_logger = _LoggingConfig.get_logger
