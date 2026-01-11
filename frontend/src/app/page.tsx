import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4 py-12">
      <div className="w-full max-w-md space-y-8 text-center">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Taskie</h1>
          <p className="mt-2 text-gray-600">Manage your tasks with ease</p>
        </div>

        <div className="space-y-4">
          <Link
            href="/auth/signin"
            className="block w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
          >
            Sign In
          </Link>
          <Link
            href="/auth/signup"
            className="block w-full rounded-lg bg-gray-200 px-4 py-2 font-medium text-gray-900 hover:bg-gray-300"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </main>
  )
}
