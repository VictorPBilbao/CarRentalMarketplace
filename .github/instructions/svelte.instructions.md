---
description: "Use when writing or refactoring Svelte frontend code. Enforces modern Svelte 5 rune-based patterns and avoids legacy Svelte syntax."
applyTo: "frontend/src/**/*.svelte"
---

# Svelte 5 Rune Standards

- Use Svelte 5 rune-based reactivity in new and modified components.
- Prefer:
    - `$state(...)` for local mutable state
    - `$derived(...)` for derived values
    - `$effect(...)` for reactive side effects
    - `$props()` for component props
- Avoid legacy patterns in new code:
    - Avoid `export let` for props
    - Avoid `$:` reactive statements when a rune alternative is clearer
- Keep component logic strongly typed where TypeScript is available.
- Prefer composable, small components and colocated domain logic in `frontend/src/lib`.

## Example

```svelte
<script lang="ts">
  let { initialCount = 0 }: { initialCount?: number } = $props();
  let count = $state(initialCount);
  let doubled = $derived(count * 2);

  $effect(() => {
    console.log('count changed', count);
  });
</script>

<button onclick={() => count += 1}>
  {count} / {doubled}
</button>
```
