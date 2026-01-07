import React from 'react';

const TestPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🎨 Tailwind v4 Test
        </h1>
        
        <p className="text-gray-600 mb-6">
          If you can see this styled properly, Tailwind CSS is working!
        </p>
        
        <div className="space-y-4">
          {/* Button Test */}
          <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors">
            Click Me (Hover Effect)
          </button>
          
          {/* Input Test */}
          <input 
            type="text" 
            placeholder="Type something..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          
          {/* Card Test */}
          <div className="bg-gradient-to-r from-pink-500 to-orange-500 p-6 rounded-xl text-white">
            <p className="font-semibold">Gradient Background</p>
            <p className="text-sm opacity-90">This should have a gradient!</p>
          </div>
          
          {/* Grid Test */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-red-500 h-20 rounded-lg"></div>
            <div className="bg-green-500 h-20 rounded-lg"></div>
            <div className="bg-blue-500 h-20 rounded-lg"></div>
          </div>
          
          {/* Flex Test */}
          <div className="flex items-center justify-between bg-gray-100 p-4 rounded-lg">
            <span className="text-gray-700">Flexbox Test</span>
            <span className="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm">
              Badge
            </span>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 text-sm text-center">
            ✅ If you see all these styles, Tailwind is working perfectly!
          </p>
        </div>
      </div>
    </div>
  );
};

export default TestPage;