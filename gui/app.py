import customtkinter as ctk
from gui.views import TensionView, CompressionView, ConnectionView, FlexureView, WeldView, CombinedView, SectionView, BasePlateView, MomentConnectionView

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Civil Engineering - Steel Calculator (SNI)")
        self.geometry("900x600")
        self.resizable(False, False)

        # Grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkScrollableFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        # self.sidebar_frame.grid_rowconfigure(11, weight=1) # No longer needed/effective directly on ScrollableFrame outer shell usually

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Civil Engineering", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_tension = ctk.CTkButton(self.sidebar_frame, text="Tension Member", command=self.show_tension)
        self.btn_tension.grid(row=1, column=0, padx=20, pady=10)

        self.btn_compression = ctk.CTkButton(self.sidebar_frame, text="Compression Member", command=self.show_compression)
        self.btn_compression.grid(row=2, column=0, padx=20, pady=10)

        self.btn_flexure = ctk.CTkButton(self.sidebar_frame, text="Flexural Member (Beam)", command=self.show_flexure)
        self.btn_flexure.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_combined = ctk.CTkButton(self.sidebar_frame, text="Beam-Column (Combined)", command=self.show_combined)
        self.btn_combined.grid(row=4, column=0, padx=20, pady=10)

        self.btn_connections = ctk.CTkButton(self.sidebar_frame, text="Bolt Connections", command=self.show_connections)
        self.btn_connections.grid(row=5, column=0, padx=20, pady=10)

        self.btn_welds = ctk.CTkButton(self.sidebar_frame, text="Welded Connections", command=self.show_welds)
        self.btn_welds.grid(row=6, column=0, padx=20, pady=10)

        self.btn_moment = ctk.CTkButton(self.sidebar_frame, text="Moment End Plate", command=self.show_moment)
        self.btn_moment.grid(row=7, column=0, padx=20, pady=10)
        
        self.btn_baseplate = ctk.CTkButton(self.sidebar_frame, text="Base Plate", command=self.show_baseplate)
        self.btn_baseplate.grid(row=8, column=0, padx=20, pady=10)
        
        self.btn_section = ctk.CTkButton(self.sidebar_frame, text="Profile Visualizer", command=self.show_section)
        self.btn_section.grid(row=9, column=0, padx=20, pady=10)
        
        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=11, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=12, column=0, padx=20, pady=(10, 20))

        # Main Content
        self.current_view = None
        self.show_tension()

    def show_view(self, view_class):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self)
        self.current_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_tension(self):
        self.show_view(TensionView)

    def show_compression(self):
        self.show_view(CompressionView)

    def show_connections(self):
        self.show_view(ConnectionView)

    def show_flexure(self):
        self.show_view(FlexureView)

    def show_welds(self):
        self.show_view(WeldView)

    def show_combined(self):
        self.show_view(CombinedView)

    def show_section(self):
        self.show_view(SectionView)
        
    def show_baseplate(self):
        self.show_view(BasePlateView)
        
    def show_moment(self):
        self.show_view(MomentConnectionView)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = App()
    app.mainloop()
