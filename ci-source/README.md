# ELITEX RC18 CI source overlay

The release workflow reconstructs the complete ELITEX source from the upstream base plus the frozen RC18 overlay.

Required file:

`ci-source/ELITEX_OVERLAY_RC18_8.tar.xz`

Expected SHA-256:

`52b120a01c2086e84b934ba8bb6afb692ab0568794b263f831d01da98a8a6907`

Expected local source: ELITEX RC18.8 / RC18.5 frozen tree overlay. The workflow is fail-closed: it refuses to build if the file is absent or its hash does not match.

Upstream base used only to reconstruct unchanged baseline files:
`https://github.com/jammy928/CoinExchange_CryptoExchange_Java` (`master`).

No ELITEX changes are intentionally dropped by this reconstruction. The overlay contains all build-relevant files that differ from or are additional to the baseline, plus the overlay manifest.
