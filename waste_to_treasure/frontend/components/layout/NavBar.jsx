import Link from 'next/link'
import Image from 'next/image'
import { ShoppingCart } from 'lucide-react'

export default function NavBar() {
  return (
    <header className="sticky top-0 z-50 w-full bg-white shadow-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        {/* Columna Izquierda (Logo) */}
        <div className="flex flex-1 justify-start">
          <Link href="/" className="flex-shrink-0">
            {/* Asumiendo que tu logo está en public/images/logo.svg */}
            <Image
              src="/images/LogoFondoBlanco.webp"
              alt="Waste to Treasure Logo"
              width={80}
              height={62}
              className="h-16 w-auto"
            />
          </Link>
        </div>

        {/* Columna Central (Navegación) */}
        <nav className="hidden flex-1 gap-8 md:flex">
          <Link
            href="/materials"
            className="font-inter text-base text-neutral-900 hover:text-primary-500"
          >
            Materiales
          </Link>
          <Link
            href="/products"
            className="font-inter text-base text-neutral-900 hover:text-primary-500"
          >
            Productos
          </Link>
          <Link
            href="/plans"
            className="font-inter text-base text-neutral-900 hover:text-primary-500"
          >
            Planes
          </Link>
        </nav>

        {/* Columna Derecha (Acciones) */}
        <div className="flex flex-1 items-center justify-end gap-4">
          <Link
            href="/login"
            className="hidden rounded-lg border-2 border-primary-500 px-5 py-2 text-base font-semibold text-primary-500 transition-colors hover:bg-primary-500/10 sm:block"
          >
            Iniciar sesión
          </Link>
          <Link
            href="/register"
            className="hidden rounded-lg bg-primary-500 px-5 py-2.5 text-base font-semibold text-white transition-colors hover:bg-primary-600 sm:block"
          >
            Regístrate
          </Link>
          <button
            aria-label="Carrito de compras"
            className="rounded-full p-2 text-neutral-900 hover:bg-neutral-100"
          >
            <ShoppingCart className="h-6 w-6 text-primary-500" />
          </button>
        </div>
      </div>
    </header>
  )
}