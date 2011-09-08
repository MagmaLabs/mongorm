from pysignals import Signal

pre_init = Signal(providing_args=["instance", "values"])
post_init = Signal(providing_args=["instance"])

pre_save = Signal(providing_args=["instance"])
post_save = Signal(providing_args=["instance", "created"])

pre_delete = Signal(providing_args=["instance"])
post_delete = Signal(providing_args=["instance"])
