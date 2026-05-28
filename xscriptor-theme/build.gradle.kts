plugins {
    java
    id("org.jetbrains.intellij.platform") version "2.16.0"
}

val pluginGroup: String by project
val pluginVersion: String by project
val pluginName: String by project
val platformVersion: String by project
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
        bundledPlugin("com.intellij.modules.json")
    }
}

tasks {
    java {
        toolchain {
            languageVersion = JavaLanguageVersion.of(21)
        }
    }
}

intellijPlatform {
    buildSearchableOptions = false
    pluginConfiguration {
        id = pluginGroup + ".theme"
        name = pluginName
        version = pluginVersion
        ideaVersion {
            sinceBuild = pluginSinceBuild
            untilBuild = pluginUntilBuild
        }
    }
}
