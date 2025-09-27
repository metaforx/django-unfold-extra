// TypeScript
import {defineConfig} from 'vite';
import {resolve} from 'node:path';

export default defineConfig({
    root: resolve(__dirname, 'src'),
    build: {
        outDir: resolve(__dirname, '../static/unfold_extra/js'),
        emptyOutDir: false,
        sourcemap: true,
        target: 'es2018',
        rollupOptions: {
            input: resolve(__dirname, 'js/theme-sync.js'),
            output: {
                entryFileNames: 'theme-sync.js',
                inlineDynamicImports: false,
                format: 'iife',
                manualChunks: () => {
                    return 'Any string'
                },
            }
        }
    }
});