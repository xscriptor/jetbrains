<h1>Theme Generator Script</h1>

<p>The <code>generate_themes.py</code> script reads the color palettes defined in
<code>colors.md</code> at the repository root and produces all 12 theme files
(UI themes and editor color schemes) for the Xscriptor JetBrains plugin.</p>

<h2>Quick Start</h2>

<pre><code>cd xscriptor-theme
python3 scripts/generate_themes.py</code></pre>

<p>This writes the generated files into <code>scripts/output/</code> without
touching any files under <code>src/main/resources/</code>. The output directory
contains:</p>

<table>
  <tr><th>Path</th><th>Description</th></tr>
  <tr><td><code>output/themes/*.theme.json</code></td><td>12 UI theme files (Islands Dark / Islands Light)</td></tr>
  <tr><td><code>output/colors/*.xml</code></td><td>12 editor color scheme files (Darcula / Default)</td></tr>
  <tr><td><code>output/plugin.xml</code></td><td>Reference extension entries for the real plugin.xml</td></tr>
</table>

<h2>Applying to the Plugin</h2>

<p>To write the generated files directly into <code>src/main/resources/</code>
(overwriting the real plugin files), use the <code>--apply</code> flag:</p>

<pre><code>python3 scripts/generate_themes.py --apply</code></pre>

<p>After applying, rebuild the plugin:</p>

<pre><code>./gradlew clean buildPlugin</code></pre>

<h2>How It Works</h2>

<ol>
  <li>The script parses <code>colors.md</code> at the repository root, extracting
  all 12 city-named palettes (X, Madrid, Lahabana, Miami, Paris, Tokio, Oslo,
  Helsinki, Berlin, London, Praha, Bogota).</li>
  <li>Each palette defines 16 hex colors (<code>color0</code> through
  <code>color15</code>) in a standard terminal color scheme layout.</li>
  <li>For each palette, the script derives secondary UI colors (backgrounds,
  foregrounds, borders, selections) using blend functions, then generates:
    <ul>
      <li>A <code>.theme.json</code> file with full Islands UI key overrides
      and an icon palette.</li>
      <li>A <code>.xml</code> editor color scheme with multi-language syntax
      highlighting rules.</li>
    </ul>
  </li>
  <li>The XML templates in <code>scripts/templates/</code> provide the
  structure for editor color schemes; the script performs hex color
  substitution to adapt them to each palette.</li>
</ol>

<h2>Adding or Modifying a Theme</h2>

<p>To add a new theme or change an existing one:</p>

<ol>
  <li>Edit <code>colors.md</code> at the repository root. Add a new
  <code>&lt;h2&gt;</code> section with the theme name and its 16-color JSON
  palette, or modify an existing palette.</li>
  <li>Add the theme name to the <code>DARK_THEMES</code> or
  <code>LIGHT_THEMES</code> list inside <code>generate_themes.py</code>.</li>
  <li>Run the script again.</li>
</ol>

<h2>Command-Line Options</h2>

<table>
  <tr><th>Flag</th><th>Description</th></tr>
  <tr><td><code>--output PATH</code></td><td>Custom output directory (default: <code>scripts/output/</code>)</td></tr>
  <tr><td><code>--templates PATH</code></td><td>Custom directory for XML templates (default: <code>scripts/templates/</code>)</td></tr>
  <tr><td><code>--apply</code></td><td>Write directly to <code>src/main/resources/</code></td></tr>
</table>

<h2>Requirements</h2>

<ul>
  <li>Python 3.9 or later (standard library only, no external dependencies)</li>
</ul>
