# EditorConfig Java Binding

This directory is for [EditorConfig][] Java Binding. This binding is a Java
wrapper for [EditorConfig Python Core][], made possible by [Jython][].

## EditorConfig Project

EditorConfig makes it easy to maintain the correct coding style when switching
between different text editors and between different projects.  The
EditorConfig project maintains a file format and plugins for various text
editors which allow this file format to be read and used by those editors.  For
information on the file format and supported text editors, see the
[EditorConfig website][EditorConfig].

## Build the Library and Generate the Doc

With [Ant][]:

    cd /path/to/editorconfig-core-py/java-binding
    ant && ant doc

The built jar file is in the `build` directory and the documentation is in the
`doc` directory.

## Use as a Library

A basic example:

```java
EditorConfig ec = new EditorConfig();
List<EditorConfig.OutPair> l = null;
try {
    l = ec.getProperties("/home/user/src/editorconfig-core-py/a.py");
} catch(EditorConfigException e) {
    System.out.println(e);
    System.exit(1);
}

for(int i = 0; i < l.size(); ++i) {
    System.out.println(l.get(i).getKey() + "=" + l.get(i).getVal());
}
```

A more complex example is in the `example` directory.

## Lisence

All source files of the Java binding are distributed under the PSF license. See LICENSE.txt for details.

[EditorConfig]: http://editorconfig.org
[EditorConfig Python Core]: https://github.com/editorconfig/editorconfig-core-py
[Jython]: http://www.jython.org
[Ant]: ant.apache.org