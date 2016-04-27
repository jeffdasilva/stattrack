###############################################################################
#
# Jeff's Boilerplate Build Infrastructure
#
#
###############################################################################


###############################################################################
#
# My git convenience targets
#

.PHONY: pull sync
pull sync: git-update

.PHONY: diff
diff: git-diff

.PHONY: push submit
push submit:
	$(MAKE) git-add-commit
	$(MAKE) git-push

.PHONY: revert
revert: git-reset

.PHONY: git-update
git-update:
	git pull

.PHONY: git-add-commit
git-add-commit:
	git add -u
	git commit -a

.PHONY: git-config
git-config:
	git config --global core.editor emacs

git-set-remote:
	git remote set-url origin git@github.com:jeffdasilva/stattrack.git

.PHONY: git-push
git-push:
	git push origin master

.PHONY: git-diff git-status
git-diff git-status: git-%:
	git $*

.PHONY: git-log
git-log:
	git log | head -n12

# this one is dangerous, so be careful with it
.PHONY: git-revert git-reset
git-revert git-reset:
	git reset --hard

###############################################################################
