'use client';

import React, { useState } from 'react';
import { Search, MapPin, TrendingUp, Users } from 'lucide-react';
import DemographicReport from './components/DemographicReport';

export default function Home() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError(null);
        setData(null);

        try {
            const response = await fetch(`/api/demographics?municipality=${encodeURIComponent(query)}`);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to fetch data');
            }

            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-gray-50 flex flex-col">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <TrendingUp className="h-6 w-6 text-blue-600" />
                        <h1 className="text-xl font-bold text-gray-900">Spanish Real Estate Analyzer</h1>
                    </div>
                    <nav className="flex gap-4">
                        <button className="text-sm font-medium text-gray-500 hover:text-gray-900">Demographics</button>
                        <button className="text-sm font-medium text-gray-500 hover:text-gray-900" disabled>Market (Coming Soon)</button>
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
                <div className="max-w-3xl mx-auto text-center mb-12">
                    <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                        Deep Insights for Spanish Real Estate
                    </h2>
                    <p className="mt-4 text-lg text-gray-500">
                        Access official demographic data and market comparables instantly.
                    </p>
                </div>

                {/* Search Box */}
                <div className="max-w-2xl mx-auto mb-12">
                    <form onSubmit={handleSearch} className="relative flex items-center">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Enter municipality name (e.g., Madrid, Valencia, Marbella)..."
                            className="block w-full rounded-full border-0 py-4 pl-12 pr-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-lg sm:leading-6"
                        />
                        <div className="absolute inset-y-0 left-0 flex items-center pl-4">
                            <MapPin className="h-5 w-5 text-gray-400" />
                        </div>
                        <div className="absolute inset-y-0 right-0 flex items-center pr-2">
                            <button
                                type="submit"
                                className="inline-flex items-center rounded-full bg-blue-600 px-6 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                                disabled={loading}
                            >
                                {loading ? 'Searching...' : 'Analyze'}
                            </button>
                        </div>
                    </form>
                </div>

                {/* Results Area */}
                <DemographicReport data={data} loading={loading} error={error} />

                {!data && !loading && !error && (
                    <div className="text-center text-gray-400 mt-20">
                        <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Enter a location above to see demographic insights.</p>
                    </div>
                )}
            </div>
        </main>
    );
}
