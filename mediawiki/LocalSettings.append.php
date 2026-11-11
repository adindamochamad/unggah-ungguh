<?php
# Unggah-Ungguh spike local config. Schema 0.1.0.
# This host is a local Docker instance. It is not a BASAibu wiki.

# SMW 3.2.3 emits PHP 8 deprecations; do not upgrade SMW to silence them.
error_reporting( E_ALL & ~E_DEPRECATED & ~E_USER_DEPRECATED );

wfLoadExtension( 'ParserFunctions' );
wfLoadExtension( 'SemanticMediaWiki' );
enableSemantics( 'localhost' );

$wgShowExceptionDetails = true;
$wgShowDBErrorBacktrace = true;

$wgUseSiteJs = true;
$wgAllowUserJs = false;
$wgEnableUploads = false;
$wgPingback = false;
$wgJobRunRate = 2;

$wgEmergencyContact = 'admin@localhost';
$wgPasswordSender = 'admin@localhost';

$wgGroupPermissions['*']['read'] = true;
$wgGroupPermissions['*']['edit'] = false;
$wgGroupPermissions['*']['createaccount'] = false;
$wgGroupPermissions['bot']['edit'] = true;
$wgGroupPermissions['bot']['createpage'] = true;
$wgGroupPermissions['bot']['editprotected'] = true;

$smwgQMaxInlineLimit = 200;

$internal = getenv( 'MW_INTERNAL_SERVER' );
if ( is_string( $internal ) && $internal !== '' ) {
	$wgInternalServer = $internal;
}

# Always attach the correction widget. MediaWiki:Common.js is also seeded, but
# ResourceLoader site-module cache can hide it on a fresh local wiki.
$wgHooks['BeforePageDisplay'][] = static function ( OutputPage $out, Skin $skin ) {
	$path = '/seed/Common.js';
	if ( is_readable( $path ) ) {
		$out->addInlineScript( file_get_contents( $path ) );
	}
	return true;
};
