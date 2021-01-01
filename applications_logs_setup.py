def logsetup(app, app_name):

    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler('eye_for_eye.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info(f'{app.name} startup')