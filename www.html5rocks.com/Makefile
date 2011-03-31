#
#	`make messages`
#
LANGUAGES=en de ja pt ru zh es
DJANGO_ROOT=/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/lib/django_1_2
define HEREDOC

HTML5Rocks Makefile
===================

Run `make messages` to regenerate the *.po files in `conf/locale/*`, and
`make compile` to recompile the *.mo files that gettext will use to
translate strings.

We're currently generating message files for English, German, Japanese,
Portuguese, Russian, Simplified Chinese, and Spanish. For additional
languages, edit the `LANGUAGES` variable in the Makefile.

endef
export HEREDOC

help:
	@echo "$$HEREDOC"

messages:
	@for locale in $(LANGUAGES) ; do \
		PYTHONPATH=$(DJANGO_ROOT) $(DJANGO_ROOT)/django/bin/django-admin.py makemessages -l $$locale ; \
	done

compile:
	@PYTHONPATH=$(DJANGO_ROOT) $(DJANGO_ROOT)/django/bin/django-admin.py compilemessages
