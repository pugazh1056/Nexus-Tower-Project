-- =============================================================================
-- Nexus Tower: Production & Logistics Operational Tables Extension
-- =============================================================================
-- Adds missing operational tables for production (BOM, material requirements, progress)
-- and logistics (shipment items, receipts, temperature telemetry).
-- =============================================================================

-- 1. PRODUCTION TABLES

CREATE TABLE IF NOT EXISTS public.production_bom (
    id TEXT PRIMARY KEY,
    finished_product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE RESTRICT,
    component_product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE RESTRICT,
    component_name TEXT NOT NULL,
    required_quantity_per_unit NUMERIC NOT NULL CHECK (required_quantity_per_unit >= 0),
    unit TEXT NOT NULL DEFAULT 'units',
    scrap_factor NUMERIC NOT NULL DEFAULT 0 CHECK (scrap_factor >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.production_material_requirements (
    id TEXT PRIMARY KEY,
    production_order_id UUID NOT NULL REFERENCES public.production_orders(id) ON DELETE CASCADE,
    finished_product_id UUID REFERENCES public.products(id) ON DELETE RESTRICT,
    component_product_id UUID REFERENCES public.products(id) ON DELETE RESTRICT,
    component_name TEXT,
    required_quantity NUMERIC NOT NULL CHECK (required_quantity >= 0),
    unit TEXT NOT NULL DEFAULT 'units',
    available_inventory_quantity NUMERIC NOT NULL DEFAULT 0 CHECK (available_inventory_quantity >= 0),
    material_shortage NUMERIC NOT NULL DEFAULT 0 CHECK (material_shortage >= 0),
    status TEXT NOT NULL DEFAULT 'sufficient',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.production_progress (
    id TEXT PRIMARY KEY,
    production_order_id UUID NOT NULL REFERENCES public.production_orders(id) ON DELETE CASCADE,
    production_line TEXT,
    equipment_id TEXT,
    planned_quantity NUMERIC NOT NULL DEFAULT 0 CHECK (planned_quantity >= 0),
    produced_quantity NUMERIC NOT NULL DEFAULT 0 CHECK (produced_quantity >= 0),
    production_rate NUMERIC NOT NULL DEFAULT 0 CHECK (production_rate >= 0),
    progress_percentage NUMERIC NOT NULL DEFAULT 0 CHECK (progress_percentage >= 0),
    downtime_minutes NUMERIC NOT NULL DEFAULT 0 CHECK (downtime_minutes >= 0),
    downtime_reason TEXT,
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    status TEXT NOT NULL DEFAULT 'planned',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. LOGISTICS TABLES

CREATE TABLE IF NOT EXISTS public.shipment_items (
    id TEXT PRIMARY KEY,
    shipment_id UUID NOT NULL REFERENCES public.shipments(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE RESTRICT,
    ordered_quantity NUMERIC NOT NULL CHECK (ordered_quantity >= 0),
    shipped_quantity NUMERIC NOT NULL CHECK (shipped_quantity >= 0),
    unit TEXT NOT NULL DEFAULT 'units',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.shipment_receipts (
    id TEXT PRIMARY KEY,
    shipment_id UUID NOT NULL REFERENCES public.shipments(id) ON DELETE CASCADE,
    purchase_order_id UUID REFERENCES public.purchase_orders(id) ON DELETE SET NULL,
    product_id UUID REFERENCES public.products(id) ON DELETE RESTRICT,
    received_quantity NUMERIC NOT NULL CHECK (received_quantity >= 0),
    accepted_quantity NUMERIC NOT NULL CHECK (accepted_quantity >= 0),
    rejected_quantity NUMERIC NOT NULL CHECK (rejected_quantity >= 0),
    damaged_quantity NUMERIC NOT NULL CHECK (damaged_quantity >= 0),
    partial_delivery BOOLEAN NOT NULL DEFAULT FALSE,
    receipt_date DATE,
    inspector_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.shipment_temperature_telemetry (
    id TEXT PRIMARY KEY,
    shipment_id UUID NOT NULL REFERENCES public.shipments(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ,
    temperature NUMERIC NOT NULL,
    min_allowed_temperature NUMERIC,
    max_allowed_temperature NUMERIC,
    is_excursion BOOLEAN NOT NULL DEFAULT FALSE,
    sensor_location TEXT,
    telemetry_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. INDEXES FOR PERFORMANCE

CREATE INDEX IF NOT EXISTS idx_prod_bom_finished ON public.production_bom(finished_product_id);
CREATE INDEX IF NOT EXISTS idx_prod_bom_component ON public.production_bom(component_product_id);
CREATE INDEX IF NOT EXISTS idx_prod_mat_req_order ON public.production_material_requirements(production_order_id);
CREATE INDEX IF NOT EXISTS idx_prod_prog_order ON public.production_progress(production_order_id);
CREATE INDEX IF NOT EXISTS idx_shipment_items_shipment ON public.shipment_items(shipment_id);
CREATE INDEX IF NOT EXISTS idx_shipment_items_product ON public.shipment_items(product_id);
CREATE INDEX IF NOT EXISTS idx_shipment_receipts_shipment ON public.shipment_receipts(shipment_id);
CREATE INDEX IF NOT EXISTS idx_shipment_telemetry_shipment ON public.shipment_temperature_telemetry(shipment_id);

-- 4. ROW LEVEL SECURITY (RLS) POLICIES

ALTER TABLE public.production_bom ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.production_material_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.production_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shipment_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shipment_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shipment_temperature_telemetry ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'production_bom' AND policyname = 'Allow authenticated read') THEN
        CREATE POLICY "Allow authenticated read" ON public.production_bom FOR SELECT TO authenticated USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'production_material_requirements' AND policyname = 'Allow authenticated read') THEN
        CREATE POLICY "Allow authenticated read" ON public.production_material_requirements FOR SELECT TO authenticated USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'production_progress' AND policyname = 'Allow authenticated read') THEN
        CREATE POLICY "Allow authenticated read" ON public.production_progress FOR SELECT TO authenticated USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'shipment_items' AND policyname = 'Allow authenticated read') THEN
        CREATE POLICY "Allow authenticated read" ON public.shipment_items FOR SELECT TO authenticated USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'shipment_receipts' AND policyname = 'Allow authenticated read') THEN
        CREATE POLICY "Allow authenticated read" ON public.shipment_receipts FOR SELECT TO authenticated USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'shipment_temperature_telemetry' AND policyname = 'Allow authenticated read') THEN
        CREATE POLICY "Allow authenticated read" ON public.shipment_temperature_telemetry FOR SELECT TO authenticated USING (true);
    END IF;
END $$;
