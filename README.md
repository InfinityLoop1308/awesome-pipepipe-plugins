# Awesome PipePipe Plugins

A community-curated list of third-party plugins for [PipePipe](https://github.com/InfinityLoop1308/PipePipe), plus a ready-to-use plugin repository (`index.json`).

> Plugins run code inside the app and are not reviewed by any app store. Only install plugins from authors you trust. Entries here are listed by the community and are not audited by the PipePipe maintainers.

## Use it in PipePipe

1. Open **Settings → Plugins** and enable plugins.
2. Tap **Add awesome-pipepipe-plugins repository** (shown while this repository is not added yet).
   Or add the URL manually with **Add repository**:

   ```
   https://raw.githubusercontent.com/InfinityLoop1308/awesome-pipepipe-plugins/main/index.json
   ```
3. Pick a plugin from the **Available** list and install it.
4. Restart PipePipe to activate it.

## Plugins

| Plugin | Description | Author | Source |
| ------ | ----------- | ------ | ------ |
| Twitch | Provides access to Twitch, the well-known streaming service | Jonas Mohr | https://github.com/MohrJonas/TwitchPipePipePlugin |

The official plugins live in a separate, built-in repository and do not need to be added.

## Submit your plugin

1. Build and sign your plugin. See the [plugin template](https://github.com/InfinityLoop1308/PipePipePluginTemplate) for the package format.
2. Host the `.ppp` package somewhere stable (for example a GitHub release asset).
3. Open a pull request that:
   - adds an entry to `index.json`
   - adds a row to the table above
4. Link the plugin's source code in the PR. Closed-source plugins are not accepted.

### Index entry format

```json
{
  "pluginId": "org.example.myservice",
  "name": "MyService",
  "versionCode": 3,
  "versionName": "1.2.0",
  "apiVersion": "1.0",
  "author": "Jane Doe",
  "package": "https://example.com/myservice-3.ppp",
  "sha256": "<hex sha256 of the package>",
  "signature": "<base64 Ed25519 signature of the raw sha256 digest>",
  "publicKey": "<base64 raw Ed25519 public key>",
  "description": "Short description",
  "nsfw": false
}
```

`description` and `nsfw` are optional. PipePipe pins the public key on first install and refuses updates signed with another key.

### Rules

- The plugin must do what its description says and must not collect data without disclosure.
- No malware, ads injection or tracking.
- Keep `versionCode` increasing with every release.
- Entries may be removed if the plugin is abandoned, broken or found to be harmful.

## License

The list and index are released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Each plugin keeps its own license.
