PACKAGES=memorize

test:
	bin/test $(PACKAGES) \
		--with-coverage --cover-package="$(PACKAGES)" --cover-erase

show-coverage: test
	xdg-open var/coverage/index.html

# Check code quality.
check:
	bin/pylint --rcfile .pylintrc $(PACKAGES) > var/pylint.html

show-check:
	xdg-open var/pylint.html

# Creating environment.

bootstrap.py:
	wget http://downloads.buildout.org/2/bootstrap.py

bin/buildout: bootstrap.py env
	env/bin/python bootstrap.py

buildout: bin/buildout
	bin/buildout -v

env: .virtualenv
	python2.7 .virtualenv/source/virtualenv.py env

.virtualenv:
	mkdir -p .virtualenv
	wget -c \
        https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.10.tar.gz \
        -O .virtualenv/archive.tar.gz
	tar -xvf .virtualenv/archive.tar.gz
	mv virtualenv-* .virtualenv/source

# Create source distribution.
source_dist:
	python setup.py sdist
