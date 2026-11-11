<?php
/**
 * Idempotent seed for Unggah-Ungguh schema v0.1.0.
 * Running twice with the same content creates no new revisions.
 */

$IP = getenv( 'MW_INSTALL_PATH' ) ?: '/var/www/html';
putenv( "MW_INSTALL_PATH=$IP" );
require_once "$IP/maintenance/Maintenance.php";

class SeedUnggah extends Maintenance {

	public function __construct() {
		parent::__construct();
		$this->addDescription( 'Seed UU properties, template, sample pages (schema 0.1.0)' );
	}

	public function execute() {
		$user = User::newFromName( getenv( 'MW_BOT_USER' ) ?: 'uu-bot' );
		if ( !$user || $user->getId() === 0 ) {
			$this->fatalError( 'Bot user is missing. Entrypoint should have created uu-bot.' );
		}

		foreach ( $this->pages() as $titleText => $text ) {
			$this->upsert( $titleText, $text, $user );
		}

		$ip = $GLOBALS['IP'] ?? '/var/www/html';
		$smw = "$ip/extensions/SemanticMediaWiki/maintenance/rebuildData.php";
		if ( file_exists( $smw ) ) {
			$this->output( "Rebuilding SMW data...\n" );
			passthru( 'php ' . escapeshellarg( $smw ) . ' --quiet' );
		}
		passthru( 'php ' . escapeshellarg( "$ip/maintenance/runJobs.php" ) . ' --maxjobs=200' );
		$this->output( "Seed complete (schema 0.1.0).\n" );
	}

	private function upsert( $titleText, $text, User $user ) {
		$title = Title::newFromText( $titleText );
		if ( !$title ) {
			$this->fatalError( "Bad title: $titleText" );
		}
		$page = WikiPage::factory( $title );
		$content = $page->getContent();
		$current = ( $content instanceof TextContent ) ? $content->getText() : '';
		if ( rtrim( $current, "\r\n" ) === rtrim( $text, "\r\n" ) ) {
			$this->output( "unchanged\t$titleText\n" );
			return;
		}
		$status = $page->doEditContent(
			new WikitextContent( $text ),
			'Seed Unggah-Ungguh schema 0.1.0 (bot)',
			EDIT_FORCE_BOT,
			false,
			$user
		);
		if ( !$status->isOK() ) {
			$this->fatalError( "Failed to edit $titleText: " . $status->getWikiText() );
		}
		$this->output( "wrote\t$titleText\n" );
	}

	private function pages() {
		$dir = __DIR__ . '/pages';
		$template = file_get_contents( "$dir/Template_UULabels.wiki" );
		$commonJs = file_get_contents( __DIR__ . '/Common.js' );
		$labelled = gmdate( 'Y-m-d' );

		return [
			'Property:Has register' =>
				"Unggah-Ungguh schema v0.1.0.\n\nAllowed: ngoko, madya, krama, mixed, undetermined.\n\n[[Has type::Text]]\n",
			'Property:Has dialect' =>
				"Unggah-Ungguh schema v0.1.0.\n\nAllowed: mataraman, jawa-timuran, banyumasan, undetermined.\n\n[[Has type::Text]]\n",
			'Property:Has stance' =>
				"Unggah-Ungguh schema v0.1.0.\n\nAllowed: peer, deferential, assertive, mixed, undetermined.\n\nDerived in the spike from register plus address forms only.\n\n[[Has type::Text]]\n",
			'Property:Has label state' =>
				"Unggah-Ungguh schema v0.1.0.\n\nAllowed: machine, author-confirmed, author-corrected, author-rejected.\n\n[[Has type::Text]]\n",
			'Property:Has label confidence' =>
				"Unggah-Ungguh schema v0.1.0. Machine labels only; cleared on human override.\n\n[[Has type::Number]]\n",
			'Property:Has schema version' =>
				"Unggah-Ungguh schema version string. Spike uses 0.1.0.\n\n[[Has type::Text]]\n",
			'Property:Has labelled at' =>
				"When the current labels were written.\n\n[[Has type::Date]]\n",
			'Template:UULabels' => $template,
			'MediaWiki:Common.js' => $commonJs,
			'Proposal:Contoh Krama' =>
				"Panjenengan sampun dhahar dereng?\n\n" .
				"{{UULabels\n" .
				"|register=krama\n" .
				"|dialect=mataraman\n" .
				"|stance=deferential\n" .
				"|state=machine\n" .
				"|confidence=0.72\n" .
				"|schema=0.1.0\n" .
				"|labelled=$labelled\n" .
				"}}\n",
			'Unggah-Ungguh:Query' =>
				"Pages labelled krama (schema 0.1.0):\n\n" .
				"{{#ask: [[Has register::krama]] |?Has dialect |?Has label state |?Has schema version }}\n",
		];
	}
}

$maintClass = SeedUnggah::class;
require_once RUN_MAINTENANCE_IF_MAIN;
