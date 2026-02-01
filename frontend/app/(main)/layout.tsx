"use client";

import { useState, ReactNode } from "react";
import Header from "@/app/components/Header";
import Footer from "../components/Footer";

export default function MainLayout({
    children,
}: {
    children: ReactNode;
}) {
    const [open, setOpen] = useState(false);

    return (
        <>
            <Header open={open} setOpen={setOpen} />
            {children}
        </>
    );
}
