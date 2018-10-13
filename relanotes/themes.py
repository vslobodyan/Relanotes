class Themes():
    """ Все что определяет работу с темами интерфейса и текста
    """
    rn_app = None

    themes = ['default_for_dark_system_theme', 'default_light']

    current_theme_css = 'styles/%s.css' % themes[1]

    html_theme_head = '<head><link rel="stylesheet" type="text/css" href="%s"></head>' % current_theme_css

    def __init__(self, rn_app):
        self.rn_app = rn_app