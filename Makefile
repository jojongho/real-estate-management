.PHONY: help pm-install pm-run ledger-install ledger-run notice-install notice-run

help:
	@echo "Workspace shortcuts"
	@echo "  make pm-run        # projects/property-management-core"
	@echo "  make ledger-run    # projects/building-ledger-automation"
	@echo "  make notice-run    # projects/apartment-notice-normalization"

pm-install:
	$(MAKE) -C projects/property-management-core install

pm-run:
	$(MAKE) -C projects/property-management-core run

ledger-install:
	$(MAKE) -C projects/building-ledger-automation install

ledger-run:
	$(MAKE) -C projects/building-ledger-automation run

notice-install:
	$(MAKE) -C projects/apartment-notice-normalization install

notice-run:
	$(MAKE) -C projects/apartment-notice-normalization run
