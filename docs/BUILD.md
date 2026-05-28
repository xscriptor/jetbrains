<h1>Building the Xscriptor Theme Plugin</h1>

<p>This document describes how to compile the Xscriptor Theme plugin for IntelliJ-based IDEs on different operating systems.</p>

<h2>Prerequisites</h2>

<table>
  <tr><th>Requirement</th><th>Version</th><th>Notes</th></tr>
  <tr><td>Java Development Kit (JDK)</td><td>21</td><td>Both Oracle JDK and OpenJDK are supported</td></tr>
  <tr><td>Git</td><td>Any recent</td><td>Required to clone the repository</td></tr>
</table>

<p>The build system uses Gradle via the bundled Gradle Wrapper, so no separate Gradle installation is needed.</p>

<h2>Step 1: Clone the Repository</h2>

<pre><code>git clone https://github.com/xscriptor/jetbrains.git
cd jetbrains/xscriptor-theme</code></pre>

<h2>Step 2: Build the Plugin</h2>

<h3>Linux (Arch / Ubuntu)</h3>

<p>Install Java 21:</p>

<h4>Arch Linux</h4>
<pre><code>sudo pacman -S jdk21-openjdk</code></pre>

<h4>Ubuntu</h4>
<pre><code>sudo apt update
sudo apt install openjdk-21-jdk</code></pre>

<p>Verify the installation:</p>
<pre><code>java -version</code></pre>

<p>Build the plugin using the Gradle Wrapper:</p>
<pre><code>./gradlew buildPlugin</code></pre>

<p>The resulting <code>.zip</code> distribution file will be placed at:</p>
<pre><code>build/distributions/xscriptor-theme-*.zip</code></pre>

<h3>Windows</h3>

<p>Install Java 21:</p>
<ol>
  <li>Download the OpenJDK 21 MSI installer from <a href="https://adoptium.net">Adoptium</a> or <a href="https://jdk.java.net/21/">jdk.java.net</a>.</li>
  <li>Run the installer and follow the wizard. Ensure the JDK is added to the system <code>PATH</code>.</li>
</ol>

<p>Verify the installation in Command Prompt or PowerShell:</p>
<pre><code>java -version</code></pre>

<p>Build the plugin using the Gradle Wrapper (from Command Prompt or PowerShell):</p>
<pre><code>.\gradlew.bat buildPlugin</code></pre>

<p>If PowerShell blocks script execution, use:</p>
<pre><code>cmd /c "gradlew.bat buildPlugin"</code></pre>

<p>The resulting <code>.zip</code> distribution file will be placed at:</p>
<pre><code>build\distributions\xscriptor-theme-*.zip</code></pre>

<h2>Installing the Plugin</h2>

<p>There are two ways to install the built plugin:</p>

<h3>From Disk (recommended for testing)</h3>
<ol>
  <li>Open your IntelliJ-based IDE.</li>
  <li>Navigate to <strong>File > Settings > Plugins</strong> (on Windows/Linux) or <strong>IntelliJ IDEA > Settings > Plugins</strong> (on macOS).</li>
  <li>Click the gear icon and select <strong>Install Plugin from Disk...</strong>.</li>
  <li>Select the <code>.zip</code> file from <code>build/distributions/</code>.</li>
  <li>Restart the IDE when prompted.</li>
</ol>

<h3>From JetBrains Marketplace (after publishing)</h3>
<ol>
  <li>Open <strong>File > Settings > Plugins</strong>.</li>
  <li>Switch to the <strong>Marketplace</strong> tab.</li>
  <li>Search for <strong>Xscriptor Theme</strong> and click <strong>Install</strong>.</li>
  <li>Restart the IDE when prompted.</li>
</ol>

<h2>Running the Plugin in a Sandbox IDE</h2>

<p>To test the plugin in an isolated IDE instance without installing it manually:</p>

<pre><code>./gradlew runIde</code></pre>

<p>This launches a temporary IntelliJ Community Edition instance with the plugin pre-loaded.</p>

<h2>Additional Gradle Tasks</h2>

<table>
  <tr><th>Task</th><th>Description</th></tr>
  <tr><td><code>./gradlew buildPlugin</code></td><td>Compile the plugin and produce a distributable ZIP file</td></tr>
  <tr><td><code>./gradlew runIde</code></td><td>Launch a sandbox IDE with the plugin loaded</td></tr>
  <tr><td><code>./gradlew verifyPlugin</code></td><td>Run IntelliJ Plugin Verifier checks</td></tr>
  <tr><td><code>./gradlew clean</code></td><td>Remove the build directory</td></tr>
</table>

<h2>Troubleshooting</h2>

<h3>Java version mismatch</h3>
<p>If you have multiple Java versions installed, ensure Java 21 is the active one:</p>
<pre><code>java -version                 # should show "21"
echo $JAVA_HOME               # should point to a JDK 21 installation</code></pre>

<p>On Arch Linux, you can switch the default Java version with:</p>
<pre><code>sudo archlinux-java set java-21-openjdk</code></pre>

<p>On Ubuntu, use:</p>
<pre><code>sudo update-alternatives --config java</code></pre>

<h3>Gradle wrapper permission denied (Linux)</h3>
<pre><code>chmod +x gradlew</code></pre>

<h3>Out of memory during build</h3>
<p>Set the Gradle heap size in <code>gradle.properties</code>:</p>
<pre><code>org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m</code></pre>

<h3>Windows long path issues</h3>
<p>If you encounter path length errors, enable long paths in Windows or move the project to a shorter directory path (e.g., <code>C:\dev\</code>).</p>

<h3>Build cache issues</h3>
<p>Clean the cache and rebuild:</p>
<pre><code>./gradlew clean buildPlugin --no-build-cache</code></pre>
