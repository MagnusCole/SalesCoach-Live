"use client";
import { useRouter } from "next/navigation";

export default function Page() {
  const r = useRouter();
  return (
    <main className="p-6">
      <h1 className="text-xl font-semibold">Sales Coach Live</h1>
      <p className="mt-2">Captura la pestaña de tu llamada y recibe coaching en vivo.</p>
      <button
        className="mt-4 px-4 py-2 rounded bg-black text-white"
        onClick={() => r.push("/live")}
      >
        Iniciar Coach
      </button>
    </main>
  );
}
