<!--
SPDX-FileCopyrightText: 2025 Monty / Diversio

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	// Use the modular highlight.js build so we only bundle the languages we need.
	import hljs from 'highlight.js/lib/core';
	import python from 'highlight.js/lib/languages/python';
	import javascript from 'highlight.js/lib/languages/javascript';
	import typescript from 'highlight.js/lib/languages/typescript';
	import bash from 'highlight.js/lib/languages/bash';
	import jsonLang from 'highlight.js/lib/languages/json';
	import sql from 'highlight.js/lib/languages/sql';

	import 'highlight.js/styles/github-dark-dimmed.css';

	// Register a small set of common languages that are relevant for
	// our training material. Add to this list sparingly to keep bundle
	// size reasonable.
	hljs.registerLanguage('python', python);
	hljs.registerLanguage('py', python);
	hljs.registerLanguage('javascript', javascript);
	hljs.registerLanguage('js', javascript);
	hljs.registerLanguage('typescript', typescript);
	hljs.registerLanguage('ts', typescript);
	hljs.registerLanguage('bash', bash);
	hljs.registerLanguage('sh', bash);
	hljs.registerLanguage('shell', bash);
	hljs.registerLanguage('json', jsonLang);
	hljs.registerLanguage('sql', sql);

	export let code: string;
	// Optional explicit language hint, e.g. "python", "sql".
	export let language: string | null = null;

	let codeEl: HTMLElement;

	// The backend stores questions/answers as HTML-escaped. We want to
	// highlight *code*, not literal "&gt;", so we decode entities first.
	const decodeHtml = (html: string): string => {
		if (typeof document === 'undefined') return html;
		const div = document.createElement('div');
		div.innerHTML = html;
		return div.textContent ?? html;
	};

	onMount(() => {
		if (!codeEl) return;

		const decoded = decodeHtml(code ?? '');

		// If we have an explicit language that highlight.js knows, use it
		// so that auto-detection cannot guess incorrectly.
		if (language && hljs.getLanguage(language)) {
			codeEl.textContent = decoded;
			codeEl.className = `language-${language}`;
			hljs.highlightElement(codeEl);
			return;
		}

		// Otherwise let highlight.js auto-detect.
		const result = hljs.highlightAuto(decoded);
		codeEl.innerHTML = result.value;
		if (result.language) {
			codeEl.classList.add(`language-${result.language}`);
		}
	});
</script>

<pre class="cq-code-block"><code bind:this={codeEl}></code></pre>

<style>
	.cq-code-block {
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
			'Courier New', monospace;
		font-size: 0.9rem;
		line-height: 1.35;
		background-color: rgba(0, 0, 0, 0.25);
		padding: 0.5rem 0.75rem;
		border-radius: 0.5rem;
		display: inline-block;
		max-width: min(90vw, 60rem);
		text-align: left;
		margin: 0.5rem auto 0;
	}
</style>
