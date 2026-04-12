# Recticode

This is the Python CLI for the tool Recticode.

Recticode is a cli-based platform where you:
- pull a coding challenge (a real mini codebase)
- identify and fix a bug or implement a feature
- run your own tests to verify your solution
- submit your fix



**Usage**:

```console
$ recticode [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `login`
* `whoami`
* `logout`
* `start`
* `list-challenges`
* `passed-challenges`
* `submit`

## `recticode login`

**Usage**:

```console
$ recticode login [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `recticode whoami`

**Usage**:

```console
$ recticode whoami [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `recticode logout`

**Usage**:

```console
$ recticode logout [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `recticode start`

**Usage**:

```console
$ recticode start [OPTIONS] CHALLENGE_NAME
```

**Arguments**:

* `CHALLENGE_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `recticode list-challenges`

**Usage**:

```console
$ recticode list-challenges [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `recticode passed-challenges`

**Usage**:

```console
$ recticode passed-challenges [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `recticode submit`

**Usage**:

```console
$ recticode submit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
