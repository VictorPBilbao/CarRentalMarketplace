// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
      token?: string;
      usuario?: {
        id:           string;
        nome:         string;
        email:        string;
        role:         'admin' | 'locadora' | 'filial' | 'customer';
        locadoraId:   string;
        matrizId?:    string;
        filialIds?:   string[];
        filialNames?: string[];
      };
    }
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
