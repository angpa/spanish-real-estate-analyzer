'use client';

import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';

interface DemographicData {
    municipality: string;
    populationTotal: number;
    populationSpanish: number;
    populationForeign: number;
    nationalityBreakdown: { name: string; value: number }[];
}

interface DemographicReportProps {
    data: DemographicData | null;
    loading: boolean;
    error: string | null;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export default function DemographicReport({ data, loading, error }: DemographicReportProps) {
    if (loading) {
        return (
            <div className="w-full h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="w-full p-4 bg-red-100 text-red-700 rounded-lg">
                <p>Error loading demographic data: {error}</p>
            </div>
        );
    }

    if (!data) {
        return null;
    }

    const distributionData = [
        { name: 'Española', value: data.populationSpanish },
        { name: 'Extranjera', value: data.populationForeign },
    ];

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-sm font-medium text-gray-500 uppercase">Población Total</h3>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{data.populationTotal.toLocaleString()}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-sm font-medium text-gray-500 uppercase">Españoles</h3>
                    <p className="text-3xl font-bold text-blue-600 mt-2">{data.populationSpanish.toLocaleString()}</p>
                    <p className="text-sm text-gray-400 mt-1">
                        {((data.populationSpanish / data.populationTotal) * 100).toFixed(1)}%
                    </p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-sm font-medium text-gray-500 uppercase">Extranjeros</h3>
                    <p className="text-3xl font-bold text-green-600 mt-2">{data.populationForeign.toLocaleString()}</p>
                    <p className="text-sm text-gray-400 mt-1">
                        {((data.populationForeign / data.populationTotal) * 100).toFixed(1)}%
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Distribución por Origen</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={distributionData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {distributionData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value: number | undefined) => value ? value.toLocaleString() : '0'} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Principales Nacionalidades</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={data.nationalityBreakdown}
                                layout="vertical"
                                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={100} />
                                <Tooltip formatter={(value: number | undefined) => value ? value.toLocaleString() : '0'} />
                                <Legend />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}
