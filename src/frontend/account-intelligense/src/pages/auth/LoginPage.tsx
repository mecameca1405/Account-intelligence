import React from "react";
import { Link } from "react-router-dom";

export default function LoginPage() {
  return (
    <div className="min-h-screen w-full bg-white text-slate-900">
      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
        {/* LEFT / HERO */}
        <section className="relative hidden lg:block">
          {/* Background image */}
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: "url(src/assets/brand/HPE_imgBuilding.png)" }}
          />
          {/* Dark overlay */}
          <div className="absolute inset-0 bg-slate-900/60" />

          {/* Content */}
          <div className="relative flex h-full flex-col justify-end p-12">
            <div className="max-w-xl">
              <div className="text-white">
                <div className="text-5xl font-semibold leading-none tracking-tight">
                  <img src="src/assets/brand/HPE_logoWhite.png" alt="Logo_HPE" />
                </div>
                <div className="mt-2 text-3xl font-semibold tracking-tight">
                  Account Intelligence
                </div>

                <div className="mt-8 text-lg font-medium opacity-95">
                  AI-Powered Strategic Account Platform
                </div>

                <div className="mt-14 flex items-center gap-4 text-white/90">
                  <div className="h-px w-40 bg-white/50" />
                  <span className="text-base font-semibold">www.hpe.com</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* RIGHT / FORM */}
        <section className="relative flex items-center justify-center px-6 py-10 lg:px-16">
          {/* Language pill */}
          <div className="absolute right-6 top-6">
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              <span aria-hidden>🌐</span>
              English (US)
            </button>
          </div>

          <div className="w-full max-w-xl">
            <h1 className="text-4xl font-semibold tracking-tight">Welcome!</h1>
            <p className="mt-2 text-base text-slate-600">
              Please login to your account.
            </p>

            <form className="mt-10 space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-700">
                  Email
                </label>
                <input
                  type="email"
                  autoComplete="email"
                  placeholder=""
                  className="mt-2 w-full rounded-md border border-slate-200 bg-white px-4 py-3 text-base outline-none ring-0 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700">
                  Password
                </label>
                <input
                  type="password"
                  autoComplete="current-password"
                  placeholder=""
                  className="mt-2 w-full rounded-md border border-slate-200 bg-white px-4 py-3 text-base outline-none ring-0 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                />

                <div className="mt-2 flex justify-end">
                  <a
                    href="#"
                    className="text-sm font-semibold text-emerald-700 hover:text-emerald-800 hover:underline"
                  >
                    Setup or Reset Password
                  </a>
                </div>
              </div>

              <button
                type="button"
                className="mt-2 inline-flex w-56 items-center justify-center rounded-full bg-emerald-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/30"
              >
                Login
              </button>

              <div className="pt-6">
                <div className="flex items-center gap-4">
                  <span className="text-sm text-slate-600">Or continue with</span>
                  <div className="h-px flex-1 bg-slate-200" />
                </div>
              </div>

              <div className="rounded-md bg-slate-100 px-6 py-4">
              <p className="text-sm text-gray-500">
                Don't have an account?{" "}
                <Link
                  to="/signup"
                  className="text-primary font-semibold hover:underline"
                >
                  Sign Up
                </Link>
              </p>
              </div>
            </form>
          </div>
        </section>
      </div>

      {/* Small screens: show hero text above form (optional) */}
      <div className="lg:hidden">
        {/* Si quieres que en móvil también aparezca la marca con imagen,
            dímelo y te lo adapto con un header sticky + mini hero. */}
      </div>
    </div>
  );
}