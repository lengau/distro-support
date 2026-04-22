PROJECT=distro_support
# Define when more than the main package tree requires coverage
# like is the case for snapcraft (snapcraft and snapcraft_legacy):
# COVERAGE_SOURCE="starcraft"
UV_TEST_GROUPS := "--group=dev"
UV_DOCS_GROUPS := "--group=docs"
UV_LINT_GROUPS := "--group=lint" "--group=types"
UV_TICS_GROUPS := "--group=tics"

# If you have dev dependencies that depend on your distro version, uncomment these:
# ifneq ($(wildcard /etc/os-release),)
# include /etc/os-release
# endif
# ifdef VERSION_CODENAME
# UV_TEST_GROUPS += "--group=dev-$(VERSION_CODENAME)"
# UV_DOCS_GROUPS += "--group=dev-$(VERSION_CODENAME)"
# UV_LINT_GROUPS += "--group=dev-$(VERSION_CODENAME)"
# UV_TICS_GROUPS += "--group=dev-$(VERSION_CODENAME)"
# endif

include common.mk

.PHONY: format
format: format-ruff format-codespell format-prettier  ## Run all automatic formatters

.PHONY: lint
lint: lint-ruff lint-ty lint-codespell lint-mypy lint-prettier lint-pyright lint-shellcheck lint-twine lint-uv-lockfile  ## Run all linters

.PHONY: pack
pack: pack-pip  ## Build all packages

# Find dependencies that need installing
APT_PACKAGES :=
ifeq ($(wildcard /usr/include/libxml2/libxml/xpath.h),)
APT_PACKAGES += libxml2-dev
endif
ifeq ($(wildcard /usr/include/libxslt/xslt.h),)
APT_PACKAGES += libxslt1-dev
endif

# Used for installing build dependencies in CI.
.PHONY: install-build-deps
install-build-deps: install-lint-build-deps
ifeq ($(APT_PACKAGES),)
else ifeq ($(shell which apt-get),)
	$(warning Cannot install build dependencies without apt.)
	$(warning Please ensure the equivalents to these packages are installed: $(APT_PACKAGES))
else
	sudo $(APT) install $(APT_PACKAGES)
endif

# If additional build dependencies need installing in order to build the linting env.
.PHONY: install-lint-build-deps
install-lint-build-deps: install-ty

.PHONY: lint-ty
lint-ty: install-ty
	ty check

.PHONY: install-ty
install-ty:
ifneq ($(shell which ty),)
else ifneq ($(shell which snap),)
	sudo snap install --beta astral-ty
	sudo snap alias astral-ty.ty ty
else ifneq ($(shell which uv),)
	uv tool install ty
endif

.PHONY: update
update: install-uv
	uv run tools/update.py

LXD_PROJECT ?= distro-support-tests
LXD_DISTRO ?= debian/bookworm
LXD_CONTAINER = distro-support-$(subst /,-,$(subst .,-,$(LXD_DISTRO)))
LXC = lxc --project $(LXD_PROJECT)

.PHONY: test-lxd
test-lxd:  ## Run tests in an LXD container (set LXD_DISTRO=distro/version)
	lxc project show $(LXD_PROJECT) > /dev/null 2>&1 || lxc project create $(LXD_PROJECT) -c features.images=false -c features.profiles=false
	trap '$(LXC) stop $(LXD_CONTAINER) 2>/dev/null || true' EXIT
	if $(LXC) info $(LXD_CONTAINER) > /dev/null 2>&1; then
		$(LXC) start $(LXD_CONTAINER) 2>/dev/null || true
	else
		$(LXC) launch images:$(LXD_DISTRO) $(LXD_CONTAINER)
		$(LXC) exec $(LXD_CONTAINER) -- sh -c '\
			if command -v apt-get > /dev/null 2>&1; then \
				apt-get update && apt-get install -y make curl; \
			elif command -v dnf > /dev/null 2>&1; then \
				dnf install -y make curl; \
			else \
				echo "No supported package manager found" >&2; exit 1; \
			fi'
		$(LXC) exec $(LXD_CONTAINER) -- sh -c 'curl -LsSf https://astral.sh/uv/install.sh | env HOME=/root sh'
	fi
	$(LXC) file push --recursive $(PWD) $(LXD_CONTAINER)/root/
	$(LXC) exec $(LXD_CONTAINER) --env DEBIAN_FRONTEND=noninteractive --cwd /root/distro-support -- sh -c 'PATH=/root/.local/bin:$$PATH make CI=1 SETUPTOOLS_SCM_PRETEND_VERSION=0.0 setup-tests'
	$(LXC) exec $(LXD_CONTAINER) --env DEBIAN_FRONTEND=noninteractive --cwd /root/distro-support -- sh -c 'PATH=/root/.local/bin:$$PATH make CI=1 test'
