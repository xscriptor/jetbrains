plugins {
    java
    id("org.jetbrains.intellij.platform") version "2.10.5"
}

val pluginGroup: String by project
val pluginVersion: String by project
val pluginName: String by project
val platformType: String by project
val platformVersion: String by project
val platformPlugins: String by project
val pluginSinceBuild: String by project
val pluginUntilBuild: String by project

group = pluginGroup
version = pluginVersion

repositories {
    mavenCentral()
    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    intellijPlatform {
        intellijIdea(platformVersion)
        platformPlugins.split(',')
            .map { it.trim() }
            .filter { it.isNotBlank() }
            .forEach { bundledPlugin(it) }
    }
}

tasks {
    java {
        toolchain {
            languageVersion.set(JavaLanguageVersion.of(21))
        }
    }
}

intellijPlatform {
    buildSearchableOptions = false
    pluginConfiguration {
        name = pluginName
        version = pluginVersion
        ideaVersion {
            sinceBuild = pluginSinceBuild
            untilBuild = pluginUntilBuild
        }
    }
}
