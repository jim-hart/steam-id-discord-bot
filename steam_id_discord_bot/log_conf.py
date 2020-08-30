import json
import logging
import logging.config
import os
from pathlib import Path

_HERE = Path(__file__).parent.resovle()


def _isfile(*parts):
    return os.path.isfile(os.path.join(*parts))


class _LoggingConfig:

    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = object.__new__(cls)
        return cls._singleton

    def __init__(self, config='logging.json'):
        self.project = _HERE.parent
        self.package = _HERE
        with self.project.join(config).open() as f:
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
        for name in list(self._cfg['loggers']):
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
