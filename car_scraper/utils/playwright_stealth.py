def stealth_sync(context):
    """
    Aplica técnicas simples de 'stealth' para evitar detecção por automação.
    Deve ser chamada logo após criar o BrowserContext.
    """
    context.add_init_script("""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Finge que tem plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3],
        });

        // Finge que tem idiomas configurados
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt'],
        });

        // Evita detecção por eval do iframe
        Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
            get: function () {
                return window;
            }
        });
    """)
