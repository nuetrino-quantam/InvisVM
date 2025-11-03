InvisVM

Status: Under active development — contributions welcome!

This project is an experimental sandboxing and isolation framework that integrates [Firejail](https://firejail.wordpress.com/) to provide a secure runtime environment for Linux applications.
The goal is to enhance process-level security by leveraging Linux kernel features such as namespaces, seccomp filters, and capabilities to reduce attack surfaces and privilege exposure.

***Development Status:***
This project is still under active development.
Many components, including the integration modules, documentation, and testing suites, are experimental.

We are currently seeking:

* Developers familiar with Linux security, namespace isolation, and sandboxing.
* Contributors to improve code, documentation, and test coverage.
* Reviewers to help ensure licensing and integration compliance.

If you would like to contribute, please open an issue or pull request.


***Firejail Integration***

This project makes use of the **Firejail sandbox**, a lightweight SUID program that helps contain untrusted applications by:

* Creating **private namespaces** for processes, network, and IPC.
* Applying **seccomp-bpf** syscall filtering.
* Managing **capability drops** to limit process privileges.
* Restricting **filesystem and D-Bus** access.

Integration features include:

* Automatic Firejail profile generation.
* Command-line and programmatic configuration options.
* Optional user profiles for custom security levels.

Firejail is distributed under the **GNU General Public License version 2.0 (GPL-2.0)**.
You can view Firejail’s license here:
[https://github.com/netblue30/firejail/blob/master/COPYING](https://github.com/netblue30/firejail/blob/master/COPYING)

***License***

This project is licensed under the **GNU General Public License v2.0 (GPL-2.0)**.

```
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
```

See the [LICENSE](./LICENSE) file for full text.

***Acknowledgements***

* [Firejail](https://firejail.wordpress.com/) — for providing a mature, kernel-level sandboxing solution.
* The open-source Linux security community.
* All contributors who test and review security mechanisms.

***Contributing***

Contributions are encouraged!
Please ensure that any submitted code or documentation complies with the GPL-2.0 license and does not include third-party proprietary code.
Bug reports, feature suggestions, and security audits are especially welcome.

***Disclaimer:***
This project is experimental and **not production-ready**.
It is intended for testing, research, and educational use only.
Users are responsible for verifying security and compatibility in their environments.
